""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import numpy as np
import pandas as pd
import subprocess
import argparse
import rasterio
import regex
import matplotlib.pyplot as plt
import numpy.ma as ma
from glob import glob
from sklearn.metrics import mean_squared_error, r2_score
from os.path import commonprefix
import lasBounds
from canopyCover import findCC, read_raster_and_extent


def gediCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(description=("Test data fusion model for Bonaly"))

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


class dtmCreation(object):
    """
    LVIS data handler
    """

    def __init__(self):
        """Empty for now"""
        # make arrays????
        # do all the relevant methods??

    def interpretName(self, filename):
        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"
        # summaryStats = np.empty((1, 2), dtype=str)
        # rCoords = r"[\d]+\d+[.]+\d+[_]+[\d]+\d+[.]+\d"
        noise_list = []
        nPhotons_list = []
        nPhotons_list.append(regex.findall(pattern=rNPhotons, string=filename)[0])
        noise_list.append(regex.findall(pattern=rNoise, string=filename)[0])
        print(noise_list, nPhotons_list)

    def runMapLidar(self, input, res, epsg, output):
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
            ]
        )

        print("The exit code was: %d" % create_dtm.returncode)

    def createDTM(self, folder):
        """Run maplidar command to create DTMs from ALS and simulated waveforms

        Args:
            folder str): study site name for folder path
        """
        # Retrieve files in different study site folders
        # note: does not work on different noise/pts values?
        # need to write in more for this
        self.alsPath = f"data/{folder}/raw_las"
        self.simPath = f"data/{folder}/sim_ground"

        # Create ALS dtm
        self.als_list = glob(self.alsPath + "/*.las")
        for idx, self.als_file in enumerate(self.als_list):
            self.bounds = lasBounds.lasMBR(self.als_file)
            print(
                f"working on {folder} {idx + 1} of {len(self.als_list)}, bounds = {self.bounds}"
            )
            self.epsg = lasBounds.findEPSG(folder)
            self.outname = f"data/{folder}/als_dtm/{self.bounds[0]}_{self.bounds[1]}"
            self.runMapLidar(self.als_file, 30, self.epsg, self.outname)

        # Create simulated data DTM
        self.sim_list = glob(self.simPath + "/*.las")
        # Need to extract noise/photons from filename?

        # make an array?
        ##  Folder, Bounds xy, noise, photons
        ## then append metrics to array next?
        for idx, self.sim_file in enumerate(self.sim_list):
            self.clipFile = lasBounds.clipNames(self.sim_file, ".las")
            print(
                f"working on {folder} {idx + 1} of {len(self.sim_list)}, bounds = {self.bounds}"
            )
            self.bounds = lasBounds.lasMBR(self.sim_file)
            self.epsg = lasBounds.findEPSG(folder)
            self.outname = f"data/{folder}/sim_dtm/{self.clipFile}"
            self.runMapLidar(self.sim_file, 30, self.epsg, self.outname)

    def match_files(self, folder1_files, folder2_files):
        # Dictionary to store matched files
        self.matches = {}

        # Compile a regex pattern to extract the number sequence
        self.pattern = regex.compile(r"(\d+\.\d+_\d+\.\d+)")

        # Create a dictionary for folder1 files with the extracted number sequence as keys
        self.folder1_dict = {}
        for self.file in folder1_files:
            self.match = self.pattern.search(self.file)
            if self.match:
                self.key = self.match.group(1)
                self.folder1_dict[self.key] = self.file

        # Create a dictionary for folder2 files with the extracted number sequence as keys
        self.folder2_dict = {}
        for self.file in folder2_files:
            self.match = self.pattern.search(self.file)
            if self.match:
                self.key = self.match.group(1)
                if self.key not in self.folder2_dict:
                    self.folder2_dict[self.key] = []
                self.folder2_dict[self.key].append(self.file)

        # Iterate over folder1 dictionary and find matches in folder2 dictionary
        for self.key, self.file1 in self.folder1_dict.items():
            if self.key in self.folder2_dict:
                self.matches[self.file1] = self.folder2_dict[self.key]

        return self.matches

    def rasterio_write(self, data, outname, template_raster, nodata):
        """Create output geotiff from array and pre-exisiting geotiff with rasterio

        Args:
            data (ndarray): data to convert into geotiff
            outname (str): output file name
            template_raster (geotiff): existing geotiff to replicate metadata
            nodata (int): no data value
        """

        self.raster = rasterio.open(
            outname,
            "w",
            driver="GTiff",
            height=template_raster.height,
            width=template_raster.width,
            count=1,
            dtype=data.dtype,
            crs=template_raster.crs,
            transform=template_raster.transform,
        )
        self.raster.write(data, 1)

        self.raster.nodata = nodata
        self.raster.close()
        print(f"Tiff written to {outname}")

    def calcMetrics(self, array1, array2):
        """Assess differences betwen 2 DEMs

        Args:
            array1 (array): 1st array
            array2 (array): 2nd array

        Returns:
            rmse, r2, bias, no data count: metrics
        """

        # stats expect 1d array so flatten inputs
        self.flat_arr1 = array1.flatten()
        self.flat_arr2 = array2.flatten()

        print(
            "flat 1 shape: ",
            self.flat_arr1.shape,
            "flat 2 shape: ",
            self.flat_arr2.shape,
        )

        # make mask of data points
        self.data_mask = self.flat_arr2 != 0

        # filter out no data values
        self.valid_arr1 = self.flat_arr1[self.data_mask]
        self.valid_arr2 = self.flat_arr2[self.data_mask]

        # count no data pixels
        self.no_data_count = np.sum(~self.data_mask)

        # Find proportion of pixels which have no data
        self.data_count = len(self.flat_arr1)

        if len(self.valid_arr1) == 0 or len(self.valid_arr2) == 0:
            raise ValueError("No data points found")
        # find rmse
        self.rmse = np.sqrt(mean_squared_error(self.valid_arr1, self.valid_arr2))

        # find r2
        self.r2 = r2_score(self.valid_arr1, self.valid_arr2)

        # calculate bias
        self.bias = np.mean(self.valid_arr1 - self.valid_arr2)

        return self.rmse, self.r2, self.bias, self.no_data_count, self.data_count

    def diffDTM(self, arr1, arr2, no_data_value):
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
        self.valid_mask = (arr1 != no_data_value) & (arr2 != no_data_value)

        self.result = np.full(arr1.shape, no_data_value, dtype=arr1.dtype)

        # Find difference
        self.result[self.valid_mask] = arr1[self.valid_mask] - arr2[self.valid_mask]

        return self.result

    def plotImage(self, raster, outname, folder, label, cmap):
        """Make a figure from the difference DTM

        Args:
            raster (arr): data to plot
            outname (str): output image name
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        fig1 = ax1.imshow(raster, origin="lower", cmap=cmap)
        fig.colorbar(fig1, ax=ax1, label=label)
        plt.savefig(f"figures/difference/{folder}/{outname}.png")
        plt.clf()

    def findCCov(self, folder):
        # cc arrays different shape to als arrays. likely to cause issues so taking out summary stats

        self.cc_Path = f"data/{folder}/als_canopy"
        self.cc_list = glob(self.cc_Path + "/*.tif")
        for self.cc_file in self.cc_list:
            self.clipped_cc = lasBounds.clipNames(self.cc_file, ".tif")
            self.mean_ccov, self.stdDev_ccov, self.cc_masked = findCC(self.cc_file)
            self.cc_outname = f"canopy{self.clipped_cc}"
            self.plotImage(
                self.cc_masked, self.cc_outname, folder, "Canopy Cover (%)", "Greens"
            )
            print("mean CC: ", self.mean_ccov, ", stdev CC: ", self.stdDev_ccov)

    def compareDTM(self, folder):
        """Assess accuracy of simulated DTMs

        Args:
            folder (_type_): _description_
        """

        self.alsPath = f"data/{folder}/als_dtm"
        self.simPath = f"data/{folder}/sim_dtm"

        self.als_list = glob(self.alsPath + "/*.tif")
        self.sim_list = glob(self.simPath + "/*.tif")

        # Pair up ALS and sim files so they can be compared
        matched_files = self.match_files(self.als_list, self.sim_list)

        # Define regex patterns to extract info from file names
        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"

        # Open lists to be appended to results
        noise_list = []
        nPhotons_list = []
        self.r2_list = []
        self.rmse_list = []
        self.bias_list = []
        self.file_name_saved = []
        self.noData_list = []
        self.lenData_list = []
        self.folder_list = []
        self.mean_cc_list = []
        self.stdDev_cc_list = []

        # Multiple sim files for each als
        for self.als_tif, files2 in matched_files.items():
            # Extract canopy cover from original ALS files

            # get extent of als and canopy (maybe do this in a different section???)
            masked_data1, affine1, crs1, extent1 = read_raster_and_extent(file1)
            # where extents match, matching file pairs
            # find mean, stdev canopy cover
            # append to results
            # make subplots of diff_dtm and CC

            for self.sim_tif in files2:
                self.als_open = rasterio.open(self.als_tif)
                self.sim_open = rasterio.open(self.sim_tif)

                # Save shortened file name to name things with later
                clip_match = lasBounds.clipNames(self.sim_tif, ".tif")

                # Save file name for results
                self.file_name_saved.append(clip_match)
                # extract noise and photon count vals
                nPhotons_list.append(
                    regex.findall(pattern=rNPhotons, string=self.sim_tif)[0]
                )
                noise_list.append(regex.findall(pattern=rNoise, string=self.sim_tif)[0])

                self.als_read = self.als_open.read(1)
                self.sim_read = self.sim_open.read(1)

                # check array shapes
                print(
                    "ALS shape: ",
                    self.als_read.shape,
                    " Sim shape: ",
                    self.sim_read.shape,
                )

                # If shape is wrong flag arrays
                if self.als_read.shape == self.sim_read.shape:
                    # calculate stats
                    self.RMSE, self.rSquared, self.BIAS, self.noData, self.lenData = (
                        self.calcMetrics(self.als_read, self.sim_read)
                    )
                else:
                    # Flag results at end?
                    self.RMSE = -999
                    self.rSquared = -999
                    self.BIAS = -999
                    self.noData = -999
                    self.lenData = -999

                # Check metrics look reasonable before appending to results
                if -1 <= self.rSquared <= 1:
                    self.folder_list.append(folder)
                    self.r2_list.append(self.rSquared)
                    self.rmse_list.append(self.RMSE)
                    self.bias_list.append(self.BIAS)
                    self.noData_list.append(self.noData)
                    self.lenData_list.append(self.lenData)
                    print(
                        f"RMSE is: {self.RMSE}, R² is: {self.rSquared}, bias: {self.BIAS}"
                    )

                    # create difference raster
                    self.difference = self.diffDTM(self.als_read, self.sim_read, 0)
                    self.masked_diference = ma.masked_where(
                        self.difference == 0, self.difference
                    )
                    self.plotImage(
                        self.masked_diference,
                        clip_match,
                        folder,
                        "Elevation difference(m)",
                        "Spectral",
                    )
                    self.outname = f"data/{folder}/diff_dtm/{clip_match}.tif"
                    self.rasterio_write(
                        data=self.difference,
                        outname=self.outname,
                        template_raster=self.sim_open,
                        nodata=0,
                    )
                elif self.rSquared == -999:
                    print(f"Significant errors in data, mismatched array shapes")
                    self.folder_list.append(folder)
                    self.r2_list.append(self.rSquared)
                    self.rmse_list.append(self.RMSE)
                    self.bias_list.append(self.BIAS)
                    self.noData_list.append(self.noData)
                    self.lenData_list.append(self.lenData)
                else:
                    print(f"{self.sim_tif} - {self.als_tif} has an odd r2")
                    self.folder_list.append(folder)
                    self.r2_list.append(0)
                    self.rmse_list.append(0)
                    self.bias_list.append(0)
                    self.noData_list.append(self.noData)
                    self.lenData_list.append(self.lenData)

        self.nPhotons = lasBounds.removeStrings(nPhotons_list)
        self.noise = lasBounds.removeStrings(noise_list)

        # append results to dataframe
        results = {
            "Folder": self.folder_list,
            "File": self.file_name_saved,
            "nPhotons": self.nPhotons,
            "Noise": self.noise,
            "RMSE": self.rmse_list,
            "R2": self.r2_list,
            "Bias": self.bias_list,
            "NoData_count": self.noData_list,
            "Data_count": self.lenData_list,
        }

        resultsDf = pd.DataFrame(results)
        self.outCsv = f"data/{folder}/summary_stats_{folder}.csv"
        resultsDf.to_csv(self.outCsv, index=False)
        print("Results written to: ", self.outCsv)
        # print(resultsDf)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere

    # Option to run on all sites
    if all_sites < 0:
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nourages",
            "oak_ridge",
            "paracou",
            "robson_creek",
            "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for site in study_sites:
            dtms = dtmCreation()
            # dtms.createDTM(site)
            dtms.findCCov(site)
            dtms.compareDTM(site)

    # Run on specified site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        dtms = dtmCreation()
        # dtms.createDTM(study_area)
        dtms.findCCov(study_area)
        dtms.compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
