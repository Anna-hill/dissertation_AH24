"""Functions to extract las file cooordinates and file name information"""

import laspy
import regex


def lasMBR(file):
    """Find minimum bounding rectangle of las file

    Args:
        file (str): las fiel path

    Returns:
        list: bounds
    """
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
    """Remove letters from mixed string"""

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
    """Removes full file path and extension to shorten file name

    Args:
        name (str): file path
        suffix (str): file extension

    Returns:
        str: clipped name
    """
    file = name.split("/")[-1]
    clipped = file.rstrip(suffix)
    return clipped


def append_results(results, **kwargs):
    """Append values to results dictionary

    Args:
        results (dict): dictionary for comparison results
    """
    for key, value in kwargs.items():
        results[key].append(value)


def match_files(als_files, sim_files):
    """Match ALS and sim files based on bounds in file name

    Args:
        als_files (list): als files
        sim_files (list): sim files

    Returns:
        dict: als files: sim files
    """
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
