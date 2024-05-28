""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import numpy as np
import pandas as pd
import subprocess
import argparse
import rasterio
import regex
from glob import glob
from sklearn import metrics
from os.path import commonprefix
import lasBounds


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

    def findEPSG(self, study_site):
        """Retrieves EPSG code for each study site for DTM creation

        Args:
            study_site (str): study site name

        Returns:
            Appropriate EPSG code for site
        """
        self.mapping = {
            "Bonaly": 27700,
            "hubbard_brook": 32619,
            "la_selva": 32616,
            "nourages": 32622,
            "oak_ridge": 32616,
            "paracou": 32622,
            "robson_creek": 28355,
            "wind_river": 32610,
        }
        if study_site in self.mapping:
            return self.mapping[study_site]

        return study_site

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
        self.alsPath = f"data/{folder}/als_ground"
        self.simPath = f"data/{folder}/sim_ground"

        # Create ALS dtm
        self.als_list = glob(self.alsPath + "/*.las")
        for idx, self.als_file in enumerate(self.als_list):
            self.bounds = lasBounds.lasMBR(self.als_file)
            print(
                f"working on {folder} {idx + 1} of {len(self.als_list)}, bounds = {self.bounds}"
            )
            self.epsg = self.findEPSG(folder)
            self.outname = f"data/{folder}/als_dtm/{self.bounds[0]}_{self.bounds[1]}"
            ## self.runMapLidar(self.als_file, 30, self.epsg, self.outname)

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
            self.epsg = self.findEPSG(folder)
            self.outname = f"data/{folder}/sim_dtm/{self.clipFile}"
            ## self.runMapLidar(self.sim_file, 30, self.epsg, self.outname)

    def findPairs(self, list1, list2):
        "identify files of same area based on matching coords"
        self.als_pairs = []
        self.sim_pairs = []
        for self.file1 in list1:
            self.coords1 = self.file1[:17]
            for self.file2 in list2:
                self.coords2 = self.file2[:17]
                if self.coords1 == self.coords2:
                    self.als_pairs.append(self.file1)
                    self.sim_pairs.append(self.file2)
        return self.als_pairs, self.sim_pairs, self.coords2

    def removeStrings(self, mixed_list):
        self.number_list = []
        for self.item in mixed_list:
            self.num_str = regex.findall(r"\d+", self.item)
            self.number_list.extend(map(int, self.num_str))
        return self.number_list

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

    def compareDTM(self, folder):
        """Assess accuracy of simulated DTMs

        Args:
            folder (_type_): _description_
        """
        self.alsPath = f"data/{folder}/als_dtm"
        self.simPath = f"data/{folder}/sim_dtm"

        self.als_list = glob(self.alsPath + "/*.tif")
        self.sim_list = glob(self.simPath + "/*.tif")

        # Find just the file names without folder names
        self.als_files = {file.split("/")[-1] for file in self.als_list}
        self.sim_files = {file.split("/")[-1] for file in self.sim_list}

        # Find matching pairs of files
        ##self.matching_files = self.als_files & self.sim_files
        ## self.matching_files = self.findPairs(self.als_files, self.sim_files)
        self.matching_als, self.matching_sim, self.coords = self.findPairs(
            self.als_files, self.sim_files
        )

        # print("matching files: ", self.matching_als, self.matching_sim)
        # likely source of duplicates: fix later )_:
        self.matching_filesPaths = []
        for self.match_als in self.matching_als:
            for self.match_sim in self.matching_sim:
                self.matching_filesPaths.append(
                    (
                        f"{self.alsPath}/{self.match_als}",
                        f"{self.simPath}/{self.match_sim}",
                    )
                )

        print("matching files: ", self.matching_filesPaths)
        # Where file names match, find metrics

        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"
        noise_list = []
        nPhotons_list = []
        self.r2 = []
        self.rmse_list = []
        self.file_name_saved = []
        for self.filename in self.matching_filesPaths:
            # Test case- will be perfect match as sim file is duplicate of als
            self.als_open = rasterio.open(self.filename[0])
            self.sim_open = rasterio.open(self.filename[1])
            clip_match = lasBounds.clipNames(self.filename[1], ".tif")
            self.file_name_saved.append(clip_match)
            # extract noise and photon count vals
            # self.interpretName(self.filename[1])code
            nPhotons_list.append(
                regex.findall(pattern=rNPhotons, string=self.filename[1])[0]
            )

            noise_list.append(regex.findall(pattern=rNoise, string=self.filename[1])[0])

            self.als_read = self.als_open.read(1)
            self.sim_read = self.sim_open.read(1)

            # create difference raster
            self.difference = self.als_read - self.sim_read
            self.outname = f"data/{folder}/diff_dtm/{clip_match}.tif"
            self.rasterio_write(
                data=self.difference,
                outname=self.outname,
                template_raster=self.sim_open,
                nodata=0,
            )

            # calculate stats
            self.rmse = np.sqrt(np.mean((self.sim_read - self.als_read) ** 2))
            self.rSquared = metrics.r2_score(self.als_read, self.sim_read)
            self.rmse_list.append(self.rmse)
            self.r2.append(self.rSquared)

            print(f"RMSE is: {self.rmse}, R² is: {self.rSquared}")
        nPhotons = self.removeStrings(nPhotons_list)
        noise = self.removeStrings(noise_list)
        # print(nPhotons, noise, self.rmse_list, self.r2, self.file_name_saved)

        # append results to dataframe
        results = {
            "File": self.file_name_saved,
            "nPhotons": nPhotons,
            "Noise": noise,
            "RMSE": self.rmse_list,
            "R²": self.r2,
        }

        resultsDf = pd.DataFrame(results)
        resultsDf.to_csv("summary_stats.csv", index=False)
        # print(resultsDf)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere

    # Option to run on all sites
    if all_sites > 0:
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
        print(f"working on all sites ({all_sites})")
        for site in study_sites:
            dtms = dtmCreation()
            dtms.createDTM(site)
            dtms.compareDTM(site)

    # Run on specified site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        dtms = dtmCreation()
        dtms.createDTM(study_area)
        dtms.compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
