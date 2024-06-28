""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import subprocess
import argparse
from glob import glob
import rasterio
import regex
import numpy as np
import pandas as pd
import numpy.ma as ma
from sklearn.metrics import mean_squared_error, r2_score
import lasBounds
from plotting import two_plots
from interpretMetric import read_text_file, metric_functions


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


class DtmCreation(object):
    """
    LVIS data handler
    """

    def __init__(self):
        """Empty for now"""
        pass

    def createDTM(self, folder):
        """Run maplidar command to create DTMs from ALS and simulated waveforms

        Args:
            folder str): study site name for folder path
        """
        # alsPath = f"data/{folder}/raw_las"
        simPath = f"data/{folder}/sim_ground"

        # Create simulated data DTM
        sim_list = glob(simPath + "/*.las")
        for idx, sim_file in enumerate(sim_list):
            clip_file = lasBounds.clipNames(sim_file, ".las")
            bounds = lasBounds.lasMBR(sim_file)
            print(
                f"working on {folder} {idx + 1} of {len(sim_list)}, bounds = {bounds}"
            )
            epsg = lasBounds.findEPSG(folder)
            outname = f"data/{folder}/sim_dtm/{clip_file}"
            create_dtm = subprocess.run(
                [
                    "mapLidar",
                    "-input",
                    f"{sim_file}",
                    "-res",
                    f"{30}",
                    "-epsg",
                    f"{epsg}",
                    "-DTM",
                    "-float",
                    "-output",
                    f"{outname}",
                ],
                check=True,
            )

            print("The exit code was: %d" % create_dtm.returncode)

    def read_metric_text(self, metric_file, folder):
        clip_metric = lasBounds.clipNames(metric_file, ".txt")
        outname = f"data/{folder}/als_metric/{clip_metric}"
        epsg = lasBounds.findEPSG(folder)
        coordinates, ground_values, canopy_values, slope_values = read_text_file(
            metric_file
        )
        als_ground = metric_functions(
            coordinates,
            ground_values,
            cmap="Spectral",
            caption="Elevation (m)",
            outname=f"{outname}_ground",
            epsg=epsg,
        )
        # canopy is 0-1
        als_canopy = metric_functions(
            coordinates,
            canopy_values,
            cmap="Greens",
            caption="Canopy cover (%)",
            outname=f"{outname}_canopy",
            epsg=epsg,
        )
        als_slope = metric_functions(
            coordinates,
            slope_values,
            cmap="Blues",
            caption="Slope (%) or angle",
            outname=f"{outname}_slope",
            epsg=epsg,
        )

        # ALS ground array then directly - from sim
        return als_ground, als_canopy, als_slope

    @staticmethod
    # Static methods not dependant on class itself, attributes
    def match_files(als_files, sim_files):
        # Dictionary to store matched files
        matches = {}

        # regex pattern to find coords in names
        pattern = regex.compile(r"(\d+_\d+)")

        # Dictionary for als files with coords as keys
        als_dict = {
            pattern.search(file).group(1): file
            for file in als_files
            if pattern.search(file)
        }

        # Dictionary for sim files with coords as keys
        sim_dict = {}
        for file in sim_files:
            match = pattern.search(file)
            if match:
                key = match.group(1)
                if key not in sim_dict:
                    sim_dict[key] = []
                sim_dict[key].append(file)

        # If file names match, matches key will be als name, and values will be sim files
        for key, file1 in als_dict.items():
            if key in sim_dict:
                matches[file1] = sim_dict[key]

        return matches

    @staticmethod
    def rasterio_write(data, outname, template_raster, nodata):
        """Create output geotiff from array and pre-existing geotiff with rasterio

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
    def calc_metrics(als_array, sim_array):
        """Assess differences betwen 2 DEMs

        Args:
            als_array (array): 1st array
            sim_array (array): 2nd array

        Returns:
            rmse, r2, bias, no data count: metrics
        """
        # create valid data mask; so comparison excludes nodata points

        # Is there a better way to mask?
        valid_mask = (als_array != -999) & (sim_array != 0)

        # filter out no data values
        valid_als = als_array[valid_mask]
        valid_sim = sim_array[valid_mask]

        # stats expect 1d array so flatten inputs
        # do arrays truly need to be flat???
        flat_als = valid_als.flatten()
        flat_sim = valid_sim.flatten()

        # count no data pixels
        no_data_count = np.sum(~valid_mask)

        # Find proportion of pixels which have no data
        data_count = len(flat_als)

        if len(flat_als) == 0 or len(flat_sim) == 0:
            raise ValueError("No data points found")

        # find rmse
        rmse = np.sqrt(mean_squared_error(flat_als, flat_sim))

        # find r2
        r2 = r2_score(flat_als, flat_sim)

        # calculate bias
        bias = np.mean(flat_als - flat_sim)

        # set up empty array to fill with results
        result = np.full(als_array.shape, 0, dtype=als_array.dtype)
        # Find difference
        result[valid_mask] = als_array[valid_mask] - sim_array[valid_mask]

        return rmse, r2, bias, no_data_count, data_count, result

    @staticmethod
    def canopy_cover_stats(raster_data):

        # summmarise array values
        raster_data = ma.masked_where(raster_data < 0, raster_data)
        mean_cc = np.mean(raster_data)
        std_cc = np.std(raster_data)
        return mean_cc, std_cc

    @staticmethod
    def append_results(results, **kwargs):
        for key, value in kwargs.items():
            results[key].append(value)

    #################################################################################################

    def compareDTM(self, folder):
        """Assess accuracy of simulated DTMs

        Args:
            folder (_type_): _description_
        """

        als_metric_path = f"data/{folder}/pts_metric"
        als_metric_list = glob(als_metric_path + "/*.txt")

        sim_path = f"data/{folder}/sim_dtm"
        sim_list = glob(sim_path + "/*.tif")

        # Pair up ALS and sim files so they can be compared
        # regex quicker than opening all files?
        matched_files = self.match_files(als_metric_list, sim_list)

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
            "Mean_slope": [],
            "Std_dev_slope": [],
            "NoData_count": [],
            "Data_count": [],
        }
        # canopy data - comes from metric reading function

        # Multiple sim files for each als
        for als_metric, matched_sim in matched_files.items():
            for sim_tif in matched_sim:
                # als_open = rasterio.open(als_tif)
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

                # convert matching files to arrays
                sim_read = sim_open.read(1)
                als_read, als_canopy, als_slope = self.read_metric_text(
                    als_metric, folder
                )

                # als_read = ma.masked_where(als_read < -100, als_read)

                try:
                    # If array shape is wrong add flags
                    if als_read.shape == sim_read.shape:
                        rmse, rSquared, bias, noData, lenData, difference = (
                            self.calc_metrics(als_read, sim_read)
                        )
                        # Save and plot tiff of difference with 0 values hidden
                        masked_diference = ma.masked_where(difference == 0, difference)

                        diff_outname = f"data/{folder}/diff_dtm/{clip_match}.tif"
                        self.rasterio_write(
                            data=difference,
                            outname=diff_outname,
                            template_raster=sim_open,
                            nodata=0,
                        )

                        image_name = f"figures/difference/{folder}/CC{clip_match}.png"
                        two_plots(masked_diference, als_canopy, image_name, clip_match)
                        # extract metrics from als arrays
                        mean_cc, stdDev_cc = self.canopy_cover_stats(als_canopy)
                        mean_slope, stdDev_slope = self.canopy_cover_stats(als_slope)
                    else:
                        print("Mismatched array shapes")
                        (
                            rmse,
                            rSquared,
                            bias,
                            noData,
                            lenData,
                            mean_cc,
                            stdDev_cc,
                            mean_slope,
                            stdDev_slope,
                        ) = (
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                        )

                    # save results to dictionary
                    self.append_results(
                        results,
                        Folder=folder,
                        File=file_name_saved,
                        nPhotons=nPhotons,
                        Noise=noise,
                        RMSE=rmse,
                        R2=rSquared,
                        Bias=bias,
                        Mean_Canopy_cover=mean_cc,
                        Std_dev_Canopy_cover=stdDev_cc,
                        Mean_slope=mean_slope,
                        Std_dev_slope=stdDev_slope,
                        NoData_count=noData,
                        Data_count=lenData,
                    )
                    # print(f"rmse is: {rmse}, R² is: {rSquared}, bias: {bias}")

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
        outCsv = f"data/{folder}/summary_stats_{folder}_new.csv"
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
