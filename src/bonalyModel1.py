""" Test script to try data fusion things"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import rasterio
from pyproj import Transformer
from gediHandler import gediData


def gediCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(description=("Test data fusion model for Bonaly"))

    p.add_argument(
        "--input",
        dest="inName",
        type=str,
        default="/exports/csce/datastore/geos/groups/MSCGIS/s2559258/Bonaly/sim_waves/bonaly.h5",
        help=("Input GEDI HDF5 filename"),
    )

    p.add_argument(
        "--bounds",
        dest="bounds",
        type=float,
        nargs=4,
        default=[-100000000, -100000000, 100000000000, 10000000000],
        help=("Bounds to plot between. minX minY maxX maxY"),
    )
    p.add_argument(
        "--outRoot",
        dest="outRoot",
        type=str,
        default="figures",
        help=("Output graph filename root"),
    )

    p.add_argument(
        "--metricText",
        dest="metricText",
        type=str,
        ## CHANGE to SYSDIR!
        default="data/teastMetric.metric.txt",
        help=("Write out csv files of the waveforms"),
    )
    cmdargs = p.parse_args()
    return cmdargs


if __name__ == "__main__":
    # read the command line
    cmdargs = gediCommands()
    inName = cmdargs.inName
    bounds = cmdargs.bounds
    outRoot = cmdargs.outRoot
    textFile = cmdargs.metricText

    gedi = gediData(
        filename=inName, minX=bounds[0], maxX=bounds[2], minY=bounds[1], maxY=bounds[3]
    )
    coords = gedi.writeCoords()
    gedi.readMetricText(textFile)
    srtm = rasterio.open("data/output_SRTMGL1.tif")
    slope = rasterio.open("data/slope_SRTM.tif")
    ndvi = rasterio.open("data/ndvi_bonaly.tif")
    srtm_array = srtm.read(1)
    slope_array = slope.read(1)
    ndvi_array = ndvi.read(1)
    # plt.scatter(slope_array, ndvi_array)
    plt.imshow(ndvi_array)
    plt.show()

    lon = 321352.6395
    lat = 666627.0768

    with rasterio.open("data/ndvi_bonaly.tif") as rds:
        # convert coordinate to raster projection
        transformer = Transformer.from_crs("EPSG:27700", rds.crs, always_xy=True)
        xx, yy = transformer.transform(lon, lat)

        # get value from grid
        value = list(rds.sample([(xx, yy)]))[0]
        print(f"ndvi value at {xx},{yy} = {value}")

        # https://gis.stackexchange.com/questions/358036/extracting-data-from-a-raster
