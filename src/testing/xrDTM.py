""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import subprocess
import argparse
from glob import glob
import rasterio
import regex
import xarray as xr
import rioxarray as rxr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy.ma as ma
from sklearn.metrics import mean_squared_error, r2_score
import lasBounds
from shapely.geometry import box
from unhelpful_files.canopyCover import findCC, read_raster_and_extent
from plotting import two_plots
from xrCanopy import compare_and_xarray


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
    def read_tiff(file_path, epsg):
        # Open tif file as an xarray DataArray
        array = rxr.open_rasterio(file_path)
        array.rio.write_crs(f"EPSG:{epsg}")
        return array

    @staticmethod
    def append_results(results, **kwargs):
        for key, value in kwargs.items():
            results[key].append(value)

    @staticmethod
    def check_intersection(ds1, ds2, lat_dim="y", lon_dim="x"):
        # Extract bounds for dataset 1
        lat_min_1, lat_max_1 = ds1[lat_dim].min().item(), ds1[lat_dim].max().item()
        lon_min_1, lon_max_1 = ds1[lon_dim].min().item(), ds1[lon_dim].max().item()

        # Extract bounds for dataset 2
        lat_min_2, lat_max_2 = ds2[lat_dim].min().item(), ds2[lat_dim].max().item()
        lon_min_2, lon_max_2 = ds2[lon_dim].min().item(), ds2[lon_dim].max().item()

        # Create Shapely polygons (bounding boxes)
        polygon1 = box(lon_min_1, lat_min_1, lon_max_1, lat_max_1)
        polygon2 = box(lon_min_2, lat_min_2, lon_max_2, lat_max_2)

        # Calculate the intersection
        intersection = polygon1.intersection(polygon2)

        # Calculate the areas
        area_ds1 = polygon1.area
        area_ds2 = polygon2.area
        overlap_area = intersection.area

        # Check if the overlap covers at least 90% of one of the datasets' area
        if overlap_area >= 0.9 * area_ds1 or overlap_area >= 0.9 * area_ds2:
            return True

    # match files
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

    # calc metrics

    # create dtm of difference

    # stats of canopy cover
    @staticmethod
    def canopy_cover_stats(ds, dim=["x", "y"]):
        # file path defined in containing method (compare)
        # raster_data, _, _, _ = read_raster_and_extent(file_path)
        """mask = file > 0
        masked1 = file.where(mask)
        mean_cc = np.nanmean(masked1[0].values)
        std_cc = np.nanstd(masked1[0].values)"""
        masked_ds = ds.where(ds >= 0)

        # Calculate mean and standard deviation
        mean_cc = masked_ds.mean(dim=dim).item()
        std_cc = masked_ds.std(dim=dim).item()
        return mean_cc, std_cc

    # append results to dataframe function

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
        matched_files = self.match_files(als_list, sim_list)

        # crs of file
        epsg = lasBounds.findEPSG(folder)

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
                als_array = self.read_tiff(als_tif, epsg)
                sim_array = self.read_tiff(sim_tif, epsg)

                # Save shortened file name to name things with later
                clip_match = lasBounds.clipNames(sim_tif, ".tif")

                # Save file name for results
                file_name_saved = clip_match
                # extract noise and photon count vals
                nPhotons = regex.findall(pattern=rNPhotons, string=sim_tif)[0]
                noise = regex.findall(pattern=rNoise, string=sim_tif)[0]
                nPhotons = lasBounds.removeStrings(nPhotons)
                noise = lasBounds.removeStrings(noise)

                try:
                    if als_array.shape == sim_array.shape:
                        ds_diff, rmse, rSquared, bias, noData, lenData = (
                            compare_and_xarray(als_array, sim_array)
                        )
                    else:
                        print("Mismatched array shapes")
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
                        print(f"rmse is: {rmse}, R² is: {rSquared}, bias: {bias}")
                        for canopy_file in canopy_list:
                            canopy_array = self.read_tiff(canopy_file, epsg)

                            # match files with 90% area intersection
                            if self.check_intersection(ds_diff, canopy_array) == True:
                                # Get CC stats
                                mean_cc, stdDev_cc = self.canopy_cover_stats(
                                    canopy_array
                                )
                                print(mean_cc, stdDev_cc)
                                break
                        self.append_results(
                            results,
                            Mean_Canopy_cover=mean_cc,
                            Std_dev_Canopy_cover=stdDev_cc,
                        )

                    # Options for different error cases
                    else:
                        print("Significant errors in data")
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
                            Mean_Canopy_cover=-900,
                            Std_dev_Canopy_cover=-900,
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
        # print(results)

        resultsDf = pd.DataFrame(results)
        outCsv = f"data/{folder}/summary_stats_{folder}new.csv"
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
            # dtm_creator.createDTM(site)
            dtm_creator.compareDTM(site)

    # Run on specified site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        # dtm_creator.createDTM(study_area)
        dtm_creator.compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
