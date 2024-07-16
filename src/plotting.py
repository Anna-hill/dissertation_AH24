"""Script to create maps from any input tiff file"""

# georeferencing currently not working

import time
import numpy as np

# import rasterio
from matplotlib import pyplot as plt

# import matplotlib.colors as colors
# import cartopy.crs as ccrs
from canopyCover import read_raster_and_extent
from lasBounds import removeStrings, findEPSG

# set font?


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
        origin="upper",
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

    fig2 = ax2.imshow(data2, origin="upper", cmap="Greens", vmin=0, vmax=1)
    fig.colorbar(
        fig2, ax=ax2, label="Canopy Cover (%)", orientation="horizontal", pad=0.1
    )
    fig.savefig(outname)
    plt.close()


def two_plots_test(data, data2, title):
    """Plot 2 datasets on a map as subplots

    Args:
        data (array): Data set
        data2 (array): Different data set
        outname (str): output file name
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    fig1 = ax1.imshow(data, origin="upper", cmap="Spectral", vmin=0, vmax=150)
    plt.title(title, loc="center")
    fig.colorbar(
        fig1,
        ax=ax1,
        label="Original",
        orientation="horizontal",
        pad=0.1,
    )

    ax2 = fig.add_subplot(122)

    fig2 = ax2.imshow(data2, origin="upper", cmap="Spectral", vmin=0, vmax=150)
    fig.colorbar(fig2, ax=ax2, label="Interpolated", orientation="horizontal", pad=0.1)
    plt.show()


def one_plot(data, outname, cmap, caption):
    """Make a map from a single dataset

    Args:
        data (array): Data to plot
        outname (str): Output file name
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig1 = ax1.imshow(data, origin="upper", cmap=cmap)
    fig.colorbar(fig1, ax=ax1, label=caption)

    plt.savefig(f"{outname}.png")
    print(f"Figure saved to {outname}.png")
    plt.close()


def three_D_scatter(x_var, y_var, z_var, colour, title):
    # See link below for guidance on making plots rotate - website and github?
    # https://matplotlib.org/stable/gallery/mplot3d/rotate_axes3d_sgskip.html#sphx-glr-gallery-mplot3d-rotate-axes3d-sgskip-py

    color_map = {
        site: color
        for site, color in zip(colour.unique(), plt.cm.get_cmap("Dark2").colors)
    }

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # n = 100

    # For each set of style and range settings, plot n random points in the box
    # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
    # for m, zlow, zhigh in [("o", -50, -25), ("^", -30, -5)]:
    # xs = randrange(n, 23, 32)
    # ys = randrange(n, 0, 100)
    # zs = randrange(n, zlow, zhigh)
    ax.scatter(
        x_var,
        y_var,
        z_var,
        color=color_map[colour],
    )

    ax.set_xlabel("X Label")
    ax.set_ylabel("Y Label")
    ax.set_zlabel("Z Label")
    plt.title(title)
    plt.show()


def folder_colour(study_site):
    """Retrieves EPSG code for each study site for DTM creation

    Args:
        study_site (str): study site name

    Returns:
        Assigned Hex code for each site
    """
    colours = {
        "Bonaly": "#003f5c",
        "hubbard_brook": "#2f4b7c",
        "la_selva": "#665191",
        "nouragues": "#a05195",
        "oak_ridge": "#d45087",
        "paracou": "#f95d6a",
        "robson_creek": "#ff7c43",
        "wind_river": "#ffa600",
        "test": "#665191",
    }
    if study_site in colours:
        return colours[study_site]

    # Unrecognised sites return as black
    return "#000000"


if __name__ == "__main__":
    t = time.perf_counter()

    # Load command  line arguments
    """cmdargs = getCmdArgs()
    infile = file_pseudo(cmdargs.inName)  # Use full file path to tiff

    plotOption = cmdargs.plotType
    output_path = out_pseudo(cmdargs.outPath)
    outname = f"{output_path}{cmdargs.outName}"

    file1 = "data/test/als_dtm/826000.0_1149352.8.tif"
    file2 = "data/test/als_canopy/000073_las_dns.tif"
    folder = "test"

    outname = f"figures/difference/plotting1"

    masked_data1, affine1, crs1, extent1 = read_raster_and_extent(file1)
    masked_data2, affine2, crs2, extent2 = read_raster_and_extent(file2)
    # epsg = findEPSG(folder)
    two_plots(masked_data1, masked_data2, outname, "beans")"""

    three_D_scatter()

    # Test efficiency
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
