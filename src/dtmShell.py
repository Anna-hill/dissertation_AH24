""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import subprocess
import argparse
from glob import glob
import rasterio
import regex
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy.ma as ma
from sklearn.metrics import mean_squared_error, r2_score
import lasBounds
from canopyCover import findCC, read_raster_and_extent, check_intersection
from plotting import two_plots


def gediCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(
        description=("Script to create DTMs and assess accuracy of simulated data")
    )

    p.add_argument(
        "--studyarea",
        dest="studyArea",
        type=str,
        default="Bonaly",
        help=("Study area name"),
    )

    p.add_argument(
        "--everywhere",
        dest="everyWhere",
        type=int,
        default="0",
        help=("Whether to run code on all study sites, 0 no, 1 yes"),
    )

    cmdargs = p.parse_args()
    return cmdargs


#### need epsg code function to feed into maplidar


class DtmCreation(object):
    """
    LVIS data handler
    """

    def __init__(self):
        """Empty for now"""
        pass

    """def interpretName(self, filename):
        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"
        noise_list = regex.findall(pattern=rNoise, string=filename)
        nPhotons_list = regex.findall(pattern=rNPhotons, string=filename)
        print(noise_list, nPhotons_list)"""

    @staticmethod
    # Static methods not dependant on class itself, attributes
    def runMapLidar(input, res, epsg, output):
        """Framework for mapLidar command to be run in terminal

        Args:
            input (str): input file path
            res (int): output dtm resolution
            epsg (int): output epsg code
            output (str): output file name
        """
        create_dtm = subprocess.run(
            [
                "mapLidar",
                "-input",
                f"{input}",
                "-res",
                f"{res}",
                "-epsg",
                f"{epsg}",
                "-DTM",
                "-float",
                "-output",
                f"{output}",
            ],
            check=True,
        )

        print("The exit code was: %d" % create_dtm.returncode)

    def createDTM(self, folder):
        """Run maplidar command to create DTMs from ALS and simulated waveforms

        Args:
            folder str): study site name for folder path
        """
        alsPath = f"data/{folder}/raw_las"
        simPath = f"data/{folder}/sim_ground"

        # Create ALS dtm
        als_list = glob(alsPath + "/*.las")
        for idx, als_file in enumerate(als_list):
            bounds = lasBounds.lasMBR(als_file)
            print(
                f"working on {folder} {idx + 1} of {len(als_list)}, bounds = {bounds}"
            )
            epsg = lasBounds.findEPSG(folder)
            outname = f"data/{folder}/als_dtm/{bounds[0]}_{bounds[1]}"
            self.runMapLidar(als_file, 30, epsg, outname)

        # Create simulated data DTM
        sim_list = glob(simPath + "/*.las")
        for idx, sim_file in enumerate(sim_list):
            clip_file = lasBounds.clipNames(sim_file, ".las")
            print(
                f"working on {folder} {idx + 1} of {len(sim_list)}, bounds = {bounds}"
            )
            bounds = lasBounds.lasMBR(sim_file)
            epsg = lasBounds.findEPSG(folder)
            outname = f"data/{folder}/sim_dtm/{clip_file}"
            self.runMapLidar(sim_file, 30, epsg, outname)

    @staticmethod
    def match_files(folder1_files, folder2_files):
        # Dictionary to store matched files
        matches = {}

        # Compile a regex pattern to extract the number sequence
        pattern = regex.compile(r"(\d+\.\d+_\d+\.\d+)")

        # Create a dictionary for folder1 files with the extracted number sequence as keys
        folder1_dict = {
            pattern.search(file).group(1): file
            for file in folder1_files
            if pattern.search(file)
        }

        # Create a dictionary for folder2 files with the extracted number sequence as keys
        folder2_dict = {}
        for file in folder2_files:
            match = pattern.search(file)
            if match:
                key = match.group(1)
                if key not in folder2_dict:
                    folder2_dict[key] = []
                folder2_dict[key].append(file)

        # Iterate over folder1 dictionary and find matches in folder2 dictionary
        for key, file1 in folder1_dict.items():
            if key in folder2_dict:
                matches[file1] = folder2_dict[key]

        return matches

    @staticmethod
    def rasterio_write(data, outname, template_raster, nodata):
        """Create output geotiff from array and pre-exisiting geotiff with rasterio

        Args:
            data (ndarray): data to convert into geotiff
            outname (str): output file name
            template_raster (geotiff): existing geotiff to replicate metadata
            nodata (int): no data value
        """

        with rasterio.open(
            outname,
            "w",
            driver="GTiff",
            height=template_raster.height,
            width=template_raster.width,
            count=1,
            dtype=data.dtype,
            crs=template_raster.crs,
            transform=template_raster.transform,
        ) as raster:
            raster.write(data, 1)
            raster.nodata = nodata
        print(f"Tiff written to {outname}")

    @staticmethod
    def calc_metrics(array1, array2):
        """Assess differences betwen 2 DEMs

        Args:
            array1 (array): 1st array
            array2 (array): 2nd array

        Returns:
            rmse, r2, bias, no data count: metrics
        """

        # stats expect 1d array so flatten inputs
        flat_arr1 = array1.flatten()
        flat_arr2 = array2.flatten()

        # make mask of data points
        data_mask = flat_arr2 != 0

        # filter out no data values
        valid_arr1 = flat_arr1[data_mask]
        valid_arr2 = flat_arr2[data_mask]

        # count no data pixels
        no_data_count = np.sum(~data_mask)

        # Find proportion of pixels which have no data
        data_count = len(flat_arr1)

        if len(valid_arr1) == 0 or len(valid_arr2) == 0:
            raise ValueError("No data points found")

        # find rmse
        rmse = np.sqrt(mean_squared_error(valid_arr1, valid_arr2))

        # find r2
        r2 = r2_score(valid_arr1, valid_arr2)

        # calculate bias
        bias = np.mean(valid_arr1 - valid_arr2)

        return rmse, r2, bias, no_data_count, data_count

    @staticmethod
    def diff_dtm(arr1, arr2, no_data_value):
        """Create tif of difference between 2 DEMs

        Args:
            arr1 (array): 1st array
            arr2 (array): 2nd array
            no_data_value (int): value of no data pixels

        Returns:
            _type_: _description_
        """

        # Check arrays have same shape
        assert arr1.shape == arr2.shape
        # create valid data mask; so comparsion excludes nodata points
        valid_mask = (arr1 != no_data_value) & (arr2 != no_data_value)
        # set up empty array to fill with results
        result = np.full(arr1.shape, no_data_value, dtype=arr1.dtype)
        # Find difference
        result[valid_mask] = arr1[valid_mask] - arr2[valid_mask]

        return result

    @staticmethod
    def plot_image(raster, outname, folder, label, cmap):
        # save to plotting
        """Make a figure from the difference DTM

        Args:
            raster (arr): data to plot
            outname (str): output image name
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        # Check whether lower origin is appropriate
        # also add georeferencing
        fig1 = ax1.imshow(raster, origin="lower", cmap=cmap)
        fig.colorbar(fig1, ax=ax1, label=label)
        plt.savefig(f"figures/difference/{folder}/{outname}.png")
        plt.clf()

    @staticmethod
    def canopy_cover_stats(file_path):
        # file path defined in containing method (compare)
        raster_data, _, _, _ = read_raster_and_extent(file_path)
        mean_cc = np.mean(raster_data)
        std_cc = np.std(raster_data)
        return raster_data, mean_cc, std_cc

    @staticmethod
    def append_results(results, **kwargs):
        for key, value in kwargs.items():
            results[key].append(value)

    def compareDTM(self, folder):
        """Assess accuracy of simulated DTMs

        Args:
            folder (_type_): _description_
        """

        als_path = f"data/{folder}/als_dtm"
        sim_path = f"data/{folder}/sim_dtm"
        canopy_path = f"data/{folder}/als_canopy"

        als_list = glob(als_path + "/*.tif")
        sim_list = glob(sim_path + "/*.tif")
        canopy_list = glob(canopy_path + "/*.tif")

        # Pair up ALS and sim files so they can be compared
        # regex quicker than opening all files?
        matched_files = self.match_files(als_list, sim_list)

        # Define regex patterns to extract info from file names
        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"

        # Open lists to be appended to results
        results = {
            "Folder": [],
            "File": [],
            "nPhotons": [],
            "Noise": [],
            "RMSE": [],
            "R2": [],
            "Bias": [],
            "Mean_Canopy_cover": [],
            "Std_dev_Canopy_cover": [],
            "NoData_count": [],
            "Data_count": [],
        }

        # Multiple sim files for each als
        for als_tif, matched_sim in matched_files.items():

            for sim_tif in matched_sim:
                als_open = rasterio.open(als_tif)
                sim_open = rasterio.open(sim_tif)

                # Save shortened file name to name things with later
                clip_match = lasBounds.clipNames(sim_tif, ".tif")

                # Save file name for results
                # file_name_saved.append(clip_match)
                file_name_saved = clip_match

                # extract noise and photon count vals
                nPhotons = regex.findall(pattern=rNPhotons, string=sim_tif)[0]
                noise = regex.findall(pattern=rNoise, string=sim_tif)[0]
                nPhotons = lasBounds.removeStrings(nPhotons)
                noise = lasBounds.removeStrings(noise)

                als_read = als_open.read(1)
                sim_read = sim_open.read(1)

                try:
                    # If array shape is wrong add flags
                    if als_read.shape == sim_read.shape:
                        rmse, rSquared, bias, noData, lenData = self.calc_metrics(
                            als_read, sim_read
                        )
                    else:
                        rmse, rSquared, bias, noData, lenData = (
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                        )

                    # Set default values to ensure df results same len
                    mean_cc = -999
                    stdDev_cc = -999
                    # If metric values look reasonable, save results
                    if -1 <= rSquared <= 1:
                        self.append_results(
                            results,
                            Folder=folder,
                            File=file_name_saved,
                            nPhotons=nPhotons,
                            Noise=noise,
                            RMSE=rmse,
                            R2=rSquared,
                            Bias=bias,
                            NoData_count=noData,
                            Data_count=lenData,
                        )
                        # print(f"rmse is: {rmse}, R² is: {rSquared}, bias: {bias}")

                        # Save and plot tiff of difference with 0 values hidden
                        difference = self.diff_dtm(als_read, sim_read, 0)
                        masked_diference = ma.masked_where(difference == 0, difference)
                        # self.plot_image(masked_diference,clip_match,folder,"Elevation difference(m)","Spectral",)
                        diff_outname = f"data/{folder}/diff_dtm/{clip_match}.tif"
                        self.rasterio_write(
                            data=difference,
                            outname=diff_outname,
                            template_raster=sim_open,
                            nodata=0,
                        )
                        # find bounds
                        diff_extents = read_raster_and_extent(diff_outname)[3]

                        # find corresponding canopy cover file:
                        for canopy_file in canopy_list:
                            canopy_cover_extents = read_raster_and_extent(canopy_file)[
                                3
                            ]

                            # match files with 90% area intersection
                            if (
                                check_intersection(diff_extents, canopy_cover_extents)
                                == True
                            ):
                                # Get CC stats
                                canopy_array, mean_cc, stdDev_cc = (
                                    self.canopy_cover_stats(canopy_file)
                                )
                                # print("mean CC: ", mean_cc, ", stdev CC: ", stdDev_cc)
                                image_name = (
                                    f"figures/difference/{folder}/CC{clip_match}.png"
                                )
                                two_plots(
                                    masked_diference,
                                    canopy_array,
                                    image_name,
                                    clip_match,
                                )
                                break

                        self.append_results(
                            results,
                            Mean_Canopy_cover=mean_cc,
                            Std_dev_Canopy_cover=stdDev_cc,
                        )

                        # need to append no data value even if no interection, but at this point in the loop will have too many iterations

                    # Options for different error cases
                    else:
                        print("Significant errors in data, mismatched array shapes")
                        self.append_results(
                            results,
                            Folder=folder,
                            File=file_name_saved,
                            nPhotons=nPhotons,
                            Noise=noise,
                            RMSE=rmse,
                            R2=rSquared,
                            Bias=bias,
                            NoData_count=noData,
                            Data_count=lenData,
                            Mean_Canopy_cover=-999,
                            Std_dev_Canopy_cover=-999,
                        )
                except ValueError as e:
                    print(f"{sim_tif} ignored due to error: {e}")
                    continue

        print(
            len(results["Folder"]),
            len(results["File"]),
            len(results["nPhotons"]),
            len(results["Noise"]),
            len(results["RMSE"]),
            len(results["R2"]),
            len(results["Bias"]),
            len(results["Mean_Canopy_cover"]),
            len(results["Std_dev_Canopy_cover"]),
            len(results["NoData_count"]),
            len(results["Data_count"]),
        )

        resultsDf = pd.DataFrame(results)
        outCsv = f"data/{folder}/summary_stats_{folder}.csv"
        resultsDf.to_csv(outCsv, index=False)
        print("Results written to: ", outCsv)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere

    dtm_creator = DtmCreation()

    # Option to run on all sites
    if all_sites < 0:
        study_sites = [
            "Bonaly",
            "paracou",
            "oak_ridge",
            "nouragues",
            "la_selva",
            "hubbard_brook",
            "robson_creek",
            "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for site in study_sites:
            dtm_creator.createDTM(site)
            dtm_creator.compareDTM(site)

    # Run on specified site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        dtm_creator.createDTM(study_area)
        dtm_creator.compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
