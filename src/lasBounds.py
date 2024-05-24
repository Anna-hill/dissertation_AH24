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
        MBR.append(minXyz)
    for maxXyz in las.header.max[0:2]:
        MBR.append(maxXyz)
    # print(MBR)
    return MBR


def clipNames(name, suffix):
    file = name.split("/")[-1]
    clipped = file.rstrip(suffix)
    return clipped


def interpretName():
    filePath = f"data/Bonaly/sim_las"

    file_list = glob(filePath + "/*.pts")

    rNPhotons = r"[p]+\d+"
    rNoise = r"[n]+\d+"
    # summaryStats = np.empty((1, 2), dtype=str)
    # rCoords = r"[\d]+\d+[.]+\d+[_]+[\d]+\d+[.]+\d"
    noise_list = []
    nPhotons_list = []
    for file in file_list:
        nPhotons_list.append(regex.findall(pattern=rNPhotons, string=file)[0])
        noise_list.append(regex.findall(pattern=rNoise, string=file)[0])
    print(noise_list, nPhotons_list)
    # need to strip n, p, then append to dataframe? (headers useful)


if __name__ == "__main__":
    # lasMBR("data/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las")
    # name = clipNames("data/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las", ".las")
    # print(name)
    interpretName()
