"""Script to create maps from any input tiff file"""

# georeferencing currently not working

import time
import numpy as np
import rasterio
from matplotlib import pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
from canopyCover import read_raster_and_extent
from lasBounds import removeStrings, findEPSG


def two_plots(data, data2, outname, title):
    """Plot 2 datasets on a map as subplots

    Args:
        data (array): Data set
        data2 (array): Different data set
        outname (str): output file name
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    fig1 = ax1.imshow(
        data,
        origin="lower",
        cmap="Spectral",
    )
    plt.title(title, loc="center")
    fig.colorbar(
        fig1,
        ax=ax1,
        label="Elevation difference (m)",
        orientation="horizontal",
        pad=0.1,
    )

    ax2 = fig.add_subplot(122)

    fig2 = ax2.imshow(
        data2,
        origin="lower",
        cmap="Greens",
    )
    fig.colorbar(
        fig2, ax=ax2, label="Canopy Cover (%)", orientation="horizontal", pad=0.1
    )
    fig.savefig(outname)
    fig.clf()


def one_plot(data, outname):
    """Make a map from a single dataset

    Args:
        data (array): Data to plot
        outname (str): Output file name
    """
    fdata = np.ma.masked_less(data, -998)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig1 = ax1.imshow(
        fdata,
        origin="lower",
        cmap="Blues",
    )
    fig.colorbar(fig1, ax=ax1, label="Elevation (m)")

    plt.savefig(f"{outname}.png")
    plt.clf()
    print(f"Figure saved to {outname}.png")


if __name__ == "__main__":
    t = time.perf_counter()

    # Load command  line arguments
    # cmdargs = getCmdArgs()
    # infile = file_pseudo(cmdargs.inName)  # Use full file path to tiff

    # plotOption = cmdargs.plotType
    # output_path = out_pseudo(cmdargs.outPath)
    # outname = f"{output_path}{cmdargs.outName}"

    file1 = "data/test/als_dtm/826000.0_1149352.8.tif"
    file2 = "data/test/als_canopy/000073_las_dns.tif"
    folder = "test"

    outname = f"{folder}/plotting1"

    masked_data1, affine1, crs1, extent1 = read_raster_and_extent(file1)
    masked_data2, affine2, crs2, extent2 = read_raster_and_extent(file2)
    epsg = findEPSG(folder)
    two_plots(masked_data1, masked_data2, outname)

    # Test efficiency
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
