""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import numpy as np
import subprocess
import argparse
import rasterio
import regex
from glob import glob
from sklearn import metrics
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

    def interpretName(self, input):
        self.rNoise = r"[n]+\d+"
        self.rNPhotons = r"[p]+\d+"
        # self.summaryStats = np.empty((1, 2), dtype=str)
        # self.rCoords = r"[\d]+\d+[.]+\d+[_]+[\d]+\d+[.]+\d"

        self.noise_list = np.array(
            (regex.findall(pattern=self.rNoise, string=input)), axis=0, dtype=str
        )
        self.nPhotons_list = np.array(
            (regex.findall(pattern=self.rNPhotons, string=input)), axis=1, dtype=str
        )
        print(self.noise_list, self.rNPhotons)

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
        self.simPath = f"data/{folder}/sim_las"

        # Create ALS dtm
        self.als_list = glob(self.alsPath + "/*.las")
        for idx, self.als_file in enumerate(self.als_list):
            self.bounds = lasBounds.lasMBR(self.als_file)
            print(
                f"working on {folder} {idx + 1} of {len(self.als_list)}, bounds = {self.bounds}"
            )
            epsg = self.findEPSG(folder)
            outname = f"data/{folder}/als_dtm/{self.bounds[0]}{self.bounds[1]}"
            ## runMapLidar(als_file, 30, epsg, outname)

        # Create simulated data DTM
        self.sim_list = glob(self.simPath + "/*.pts")
        # Need to extract noise/photons from filename?

        # make an array?
        ##  Folder, Bounds xy, noise, photons
        ## then append metrics to array next?
        for idx, self.sim_file in enumerate(self.sim_list):
            print(
                f"working on {folder} {idx + 1} of {len(self.sim_list)}, bounds = {self.bounds}"
            )
            self.bounds = lasBounds.lasMBR(self.sim_file)
            self.epsg = self.findEPSG(folder)
            self.outname = f"data/{folder}/sim_dtm/{self.bounds[0]}{self.bounds[1]}"
            ## runMapLidar(sim_file, 30, self.epsg, self.outname)

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
        self.matching_files = self.als_files & self.sim_files
        self.matching_filesPaths = [
            (f"{self.alsPath}/{filename}", f"{self.simPath}/{filename}")
            for filename in self.matching_files
        ]
        # Where file names match, find metrics
        for self.filename in self.matching_filesPaths:
            # Test case- will be perfect match as sim file is duplicate of als
            self.als_open = rasterio.open(self.filename[0])
            self.sim_open = rasterio.open(self.filename[1])
            self.als_read = self.als_open.read(1)
            self.sim_read = self.sim_open.read(1)
            self.rmse = np.sqrt(np.mean((self.sim_read - self.als_read) ** 2))
            self.rSquared = metrics.r2_score(self.als_read, self.sim_read)
            # Create new raster of difference
            # Append R2 and RMSE values to an array with noise/pts values?
            # Or a dataframe
            # Write function to plot these things on combined sctter plot

            print(f"RMSE is: {self.rmse}, R² is: {self.rSquared}")


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
