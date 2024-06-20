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


def two_plots(data, data2, outname, epsg):
    """Plot 2 datasets on a map as subplots

    Args:
        data (array): Data set
        data2 (array): Different data set
        outname (str): output file name
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(121, projection=ccrs.epsg(epsg))
    fig1 = ax1.imshow(
        data,
        origin="lower",
        transform=ccrs.epsg(epsg),
        cmap="Blues",
    )
    fig.colorbar(fig1, ax=ax1, label="Elevation (m)")
    ax1.gridlines(draw_labels=True)

    ax2 = fig.add_subplot(122, projection=ccrs.epsg(epsg))

    fig2 = ax2.imshow(
        data2,
        origin="lower",
        transform=ccrs.epsg(epsg),
        cmap="Blues",
    )
    fig.colorbar(fig2, ax=ax2, label="Elevation (m)")
    ax2.gridlines(draw_labels=True, alpha=0.5)
    fig.savefig(f"figures/difference/{outname}.png")
    fig.clf()


def plot_elev(data, outname, epsg):
    """Plot the results of the volume change calculation

    Args:
        data (2d array): Image array
        outname (str): Output file name
    """
    # https://github.com/SciTools/cartopy/issues/1946?fbclid=IwAR0iHP3qHFVclMQRqQYG5AlZwLfODSGWDkJDchUSzR55hXK_b9A8v3Uvits
    fdata = np.ma.masked_where(data == 0, data)

    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection=ccrs.epsg(epsg))

    fig1 = ax1.imshow(
        fdata,
        origin="lower",
        transform=ccrs.SouthPolarStereo(),
        norm=colors.SymLogNorm(
            linthresh=0.03, linscale=0.03, vmin=-1.0, vmax=1.0, base=10
        ),
        cmap="RdYlBu",
    )

    fig.colorbar(fig1, ax=ax1, label="Elevation Change(m) - Log Normalised")
    ax1.gridlines(draw_labels=True, alpha=0.5)

    plt.savefig(f"{outname}.png")
    plt.clf()
    print(f"Figure saved to {outname}.png")


def one_plot(data, outname, epsg):
    """Make a map from a single dataset

    Args:
        data (array): Data to plot
        outname (str): Output file name
    """
    fdata = np.ma.masked_less(data, -998)

    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection=ccrs.epsg(epsg))
    fig1 = ax1.imshow(
        fdata,
        origin="lower",
        transform=ccrs.SouthPolarStereo(),
        cmap="Blues",
    )
    ax1.gridlines(draw_labels=True, alpha=0.5)

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
    two_plots(masked_data1, masked_data2, outname, epsg)

    # Test efficiency
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
