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
    rNPhotons = r"[p]+\d+"
    rNoise = r"[n]+\d+"
    noise_list = set()
    nPhotons_list = set()
    for file in file_list:
        nPhoton = regex.findall(pattern=rNPhotons, string=file)[0]
        noise = regex.findall(pattern=rNoise, string=file)[0]

        nPhotons_list.add(nPhoton)
        noise_list.add(noise)
    return noise_list, nPhotons_list


def append_results(results, **kwargs):
    """Append values to results dictionary

    Args:
        results (dict): dictionary for comparison results
    """
    for key, value in kwargs.items():
        results[key].append(value)


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


# if __name__ == "__main__":
# lasMBR("data/paracou/raw_las/Paracou2009_284584_580489.las")
# name = clipNames("data/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las", ".las")
# print(name)
# interpretName()
