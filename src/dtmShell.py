import time
import subprocess
import argparse
import rasterio
from glob import glob
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
    alsPath = f"data/{folder}/raw_las"
    simPath = f"data/{folder}/sim_las"

    als_list = glob(alsPath + "/*.las")
    for idx, als_file in enumerate(als_list):
        bounds = lasBounds.lasMBR(als_file)
        print(f"working on {folder} {idx + 1} of {len(als_list)}, bounds = {bounds}")
        epsg = findEPSG(folder)
        outname = f"data/{folder}/als_dtm/{bounds[0]}{bounds[1]}"
        runMapLidar(als_file, 30, epsg, outname)

    sim_list = glob(simPath + "/*.las")
    for idx, sim_file in enumerate(sim_list):
        bounds = lasBounds.lasMBR(sim_file)
        print(f"working on {folder} {idx + 1} of {len(sim_list)}, bounds = {bounds}")
        outname = f"data/{folder}/sim_dtm/{bounds[0]}{bounds[1]}"
        runMapLidar(sim_file, 30, epsg, outname)


def compareDTM(folder):
    alsPath = f"data/{folder}/als_dtm"
    simPath = f"data/{folder}/sim_dtm"

    als_list = glob(alsPath + "/*.tif")
    sim_list = glob(simPath + "/*.tif")

    for als_dtm in als_list:
        for sim_dtm in sim_list:
            print(als_dtm, sim_dtm)
            if als_dtm == sim_dtm:
                als_open = rasterio.open(als_dtm)
                sim_open = rasterio.open(sim_dtm)
                print(als_open, sim_open)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere

    if all_sites > 0:
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nourages",
            "oak_ridge",
            "paracou",
            "robson_creek",
            "wind_river",  # removed for now, will run alone later
        ]
        print(f"working on all sites ({all_sites})")
        for site in study_sites:
            # createDTM(site)
            compareDTM(site)

    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        # createDTM(study_area)
        compareDTM(study_area)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
