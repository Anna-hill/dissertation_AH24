"""Test script to extract canopy cover metrics, after using lastools canopyShell.bat shell script"""

import numpy as np
import rasterio
import matplotlib.pyplot as plt
import numpy.ma as ma


def plotImage(raster):
    """Make a figure from the difference DTM

    Args:
        raster (arr): data to plot
           outname (str): output image name
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig1 = ax1.imshow(raster, origin="lower", cmap="Spectral")
    fig.colorbar(fig1, ax=ax1, label="Elevation difference(m)")
    plt.show()
    # plt.clf()


def findCC(tif):
    # cc arrays different shape to als arrays. likely to cause issues so taking out summary stats

    tif_open = rasterio.open(tif)
    tif_read = tif_open.read(1)
    print(
        "canopy cover shape: ",
        tif_read.shape,
    )
    # make mask of data points
    masked_data = ma.masked_where(tif_read == -9999, tif_read)
    # data_mask = tif_read != -9999

    # filter out no data values
    # valid_arr = tif_read[data_mask]
    # plotImage(masked_data)
    # flattening array makes calcuations easier
    flat_arr = masked_data.flatten()

    mean_CC = np.mean(flat_arr)
    stdDev_CC = np.std(flat_arr)

    # CC contains no data values (-9999)

    # What i would like this function to do:
    # find mean CC value
    # find stDev of canopy cover

    # make a canopy cover image
    # is it worth having 121 subplot where canopy cover is included against the difference???
    return mean_CC, stdDev_CC, masked_data


"""if __name__ == "__main__":
    file = "data/test/als_canopy/000073_las_dns.tif"
    mean, stddev = findCC(file)
    print("mean CC is ", mean, "StdDev is ", stddev)

    # file2 = "data/test/als_dtm/826000.0_1149352.8.tif"
    # findCC(file2)"""
