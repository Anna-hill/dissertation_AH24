# example adapted from https://laspy.readthedocs.io/en/latest/complete_tutorial.html


import laspy
import regex
from glob import glob
import numpy as np


def lasMBR(file):
    MBR = []
    las = laspy.read(file)

    # Find min max coord values form las file header and append to list
    # index p. 2 gives Z bounds, not included here
    for minXyz in las.header.min[0:2]:
        MBR.append(round(minXyz))
    for maxXyz in las.header.max[0:2]:
        MBR.append(round(maxXyz))
    return MBR


def removeStrings(str_int):

    match = regex.findall(r"\d+", str_int)
    return match[0] if match else None


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
        "nouragues": 32622,
        "oak_ridge": 32616,
        "paracou": 32622,
        "robson_creek": 28355,
        "wind_river": 32610,
        "test": 32616,
    }
    if study_site in mapping:
        return mapping[study_site]

    return study_site


def clipNames(name, suffix):
    file = name.split("/")[-1]
    clipped = file.rstrip(suffix)
    return clipped


def interpretName(file_list):
    # filePath = f"data/{folder}/sim_las"

    # file_list = glob(filePath + "/*.pts")

    rNPhotons = r"[p]+\d+"
    rNoise = r"[n]+\d+"
    # summaryStats = np.empty((1, 2), dtype=str)
    # rCoords = r"[\d]+\d+[.]+\d+[_]+[\d]+\d+[.]+\d"
    noise_list = set()
    nPhotons_list = set()
    for file in file_list:
        nPhoton = regex.findall(pattern=rNPhotons, string=file)[0]
        noise = regex.findall(pattern=rNoise, string=file)[0]
        # nPhoton = removeStrings(nPhoton)
        # noise = removeStrings(noise)
        nPhotons_list.add(nPhoton)
        noise_list.add(noise)
    return noise_list, nPhotons_list
    # need to strip n, p, then append to dataframe? (headers useful)


# if __name__ == "__main__":
# lasMBR("data/paracou/raw_las/Paracou2009_284584_580489.las")
# name = clipNames("data/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las", ".las")
# print(name)
# interpretName()
