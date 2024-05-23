""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import numpy as np
import subprocess
import argparse
import rasterio
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


def findEPSG(study_site):
    """Retrieves EPSG code for each study site for DTM creation

    Args:
        study_site (str): study site name

    Returns:
        Appropriate EPSG code for site
    """
    mapping = {
        "Bonaly": 27700,
        "hubbard_brook": 32619,
        "la_selva": 32616,
        "nourages": 32622,
        "oak_ridge": 32616,
        "paracou": 32622,
        "robson_creek": 28355,
        "wind_river": 32610,
    }
    if study_site in mapping:
        return mapping[study_site]

    # If using file path for input, will not match any alias
    # Will return file path
    return study_site


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
        ]
    )

    print("The exit code was: %d" % create_dtm.returncode)


def createDTM(folder):
    """Run maplidar command to create DTMs from ALS and simulated waveforms

    Args:
        folder str): study site name for folder path
    """
    # Retrieve files in different study site folders
    # note: does not work on different noise/pts values?
    # need to write in more for this
    alsPath = f"data/{folder}/raw_las"
    simPath = f"data/{folder}/sim_las"

    # Create ALS dtm
    als_list = glob(alsPath + "/*.las")
    for idx, als_file in enumerate(als_list):
        bounds = lasBounds.lasMBR(als_file)
        print(f"working on {folder} {idx + 1} of {len(als_list)}, bounds = {bounds}")
        epsg = findEPSG(folder)
        outname = f"data/{folder}/als_dtm/{bounds[0]}{bounds[1]}"
        runMapLidar(als_file, 30, epsg, outname)

    # Create simulated data DTM
    sim_list = glob(simPath + "/*.las")
    for idx, sim_file in enumerate(sim_list):
        bounds = lasBounds.lasMBR(sim_file)
        print(f"working on {folder} {idx + 1} of {len(sim_list)}, bounds = {bounds}")
        outname = f"data/{folder}/sim_dtm/{bounds[0]}{bounds[1]}"
        runMapLidar(sim_file, 30, epsg, outname)


def compareDTM(folder):
    """Assess accuracy of simulated DTMs

    Args:
        folder (_type_): _description_
    """
    alsPath = f"data/{folder}/als_dtm"
    simPath = f"data/{folder}/sim_dtm"

    als_list = glob(alsPath + "/*.tif")
    sim_list = glob(simPath + "/*.tif")

    # Find just the file names without folder names
    als_files = {file.split("/")[-1] for file in als_list}
    sim_files = {file.split("/")[-1] for file in sim_list}

    # Find matching pairs of files
    matching_files = als_files & sim_files
    matching_filesPaths = [
        (f"{alsPath}/{filename}", f"{simPath}/{filename}")
        for filename in matching_files
    ]
    # Where file names match, find metrics
    for filename in matching_filesPaths:
        # Test case- will be perfect match as sim file is duplicate of als
        als_open = rasterio.open(filename[0])
        sim_open = rasterio.open(filename[1])
        als_read = als_open.read(1)
        sim_read = sim_open.read(1)
        rmse = np.sqrt(np.mean((sim_read - als_read) ** 2))
        rSquared = metrics.r2_score(als_read, sim_read)
        # Create new raster of difference
        # Append R2 and RMSE values to an array with noise/pts values?
        # Or a dataframe
        # Write function to plot these things on combined sctter plot

        print(f"RMSE is: {rmse}, R² is: {rSquared}")


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
            createDTM(site)
            compareDTM(site)

    # Run on specified site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        createDTM(study_area)
        compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
