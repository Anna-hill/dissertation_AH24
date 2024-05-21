# pts_loader provides a load() method to read data from .pts files of
# point clouds
#
# --------------------------------------------------------
# pts_loader
# Licensed under The MIT License [see LICENSE.md for details]
# Copyright (C) 2017 Samuel Albanie
# --------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt


# code from :https://github.com/albanie/pts_loader/tree/master


def load(path):
    """takes as input the path to a .pts and returns a list of
    tuples of floats containing the points in in the form:
    [(x_0, y_0, z_0),
     (x_1, y_1, z_1),
     ...
     (x_n, y_n, z_n)]"""
    with open(path) as f:
        rows = [rows.strip() for rows in f]

    """Use the curly braces to find the start and end of the point data"""
    head = rows.index("{") + 1
    tail = rows.index("}")

    """Select the point data split into coordinates"""
    raw_points = rows[head:tail]
    coords_set = [point.split() for point in raw_points]

    """Convert entries from lists of strings to tuples of floats"""
    points = [tuple([float(point) for point in coords]) for coords in coords_set]
    return points


#######################################


def load_pts(path, nPhotons):
    f = np.loadtxt(path, comments="#", skiprows=1)
    # rows = [rows.strip() for rows in f]
    # print(f[0:10])
    print(f.shape)
    # x = 0, y = 1,z = 2, 3 = minTh?
    # print(f[0:10, 0:2])
    # 1 X, 2 Y, 3 Z, 4 minht, 5 WFGroundZ, 6 RH50, 7 RH60, 8 RH75, 9 RH90, 10 RH95, 11 CanopyZ, 12 canopycover, 13 shot#, 14 photon#, 15 iteration#, 16 refdem, 17 noiseInt, 18 signal, 19 ground
    x_coord = f[0:, 0]
    y_coord = f[0:, 1]
    z_coord = f[0:, 2]
    minTh = f[0:, 3]
    print(x_coord, y_coord, z_coord)
    # plt.scatter(x_coord, y_coord)
    plt.scatter(minTh[0:100], z_coord[0:100])
    plt.ylabel("Elevation (m)")
    plt.show()


if __name__ == "__main__":
    """Main block"""

    load_pts("data/Bonaly/sim_waves/metric_output/noiseMult2.pts", 100)
