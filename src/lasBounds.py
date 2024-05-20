# example adapted from https://laspy.readthedocs.io/en/latest/complete_tutorial.html


import laspy
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


# if __name__ == "__main__":
# lasMBR("data/Bonaly/raw_las/NT2065_4PPM_LAS_PHASE5.las")
