import time
import rasterio
import numpy as np
from matplotlib import pyplot as plt
from glob import glob
import pandas as pd
from scipy import stats
from lasBounds import append_results
from plotting import folder_colour
from analyseResults import analysisCommands


def find_merged(folder):
    file_path = f"data/{folder}/merged_rasters"
    # data/bonaly/merged_rasters

    canopy_list = glob(file_path + f"/canopy.tif")
    slope_list = glob(file_path + f"/slope.tif")
    diff_list = glob(file_path + f"/diff.tif")
    # print(canopy_list, slope_list, diff_list)
    return canopy_list[0], slope_list[0], diff_list[0]


def open_raster(tif):
    # open tif files as arrays and flatten
    open_tif = rasterio.open(tif)
    read_tif = open_tif.read(1)
    return read_tif


def pad_array(arr, target_shape):
    # make sure all arrays same size
    padded_arr = np.zeros(target_shape)
    padded_arr[: arr.shape[0], : arr.shape[1]] = arr
    return padded_arr


def slope_cc(folder):
    """Open tif files and return flat arrays"""

    canopy_tif, slope_tif, diff_tif = find_merged(folder)

    read_canopy = open_raster(canopy_tif)
    read_slope = open_raster(slope_tif)
    read_diff = open_raster(diff_tif)

    # find max array dims
    max_shape = (
        max(read_canopy.shape[0], read_slope.shape[0], read_diff.shape[0]),
        max(read_canopy.shape[1], read_slope.shape[1], read_diff.shape[1]),
    )

    # Resize arrays to the maximum shape
    canopy_padded = pad_array(read_canopy, max_shape)
    slope_padded = pad_array(read_slope, max_shape)
    diff_padded = pad_array(read_diff, max_shape)

    print(canopy_padded.shape, slope_padded.shape, diff_padded.shape)

    # remove 0 values and ensure same raster dims
    """combined_mask = (canopy_padded > 0) and (slope_padded > 0) and (diff_padded != 0)
    masked_canopy = np.where(combined_mask, canopy_padded, np.nan)
    masked_slope = np.where(combined_mask, slope_padded, np.nan)
    masked_diff = np.where(combined_mask, diff_padded, np.nan)"""

    # print(masked_canopy.shape, masked_slope.shape, masked_diff.shape)

    # flatten arrays for stats
    flat_canopy = canopy_padded.flatten()
    flat_slope = slope_padded.flatten()
    flat_diff = diff_padded.flatten()

    return flat_canopy, flat_slope, flat_diff


def plot_matrix(sites):

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.figsize"] = (8, 10)
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["xtick.major.size"] = 2
    plt.rcParams["xtick.major.width"] = 0.4
    plt.rcParams["xtick.major.pad"] = 2
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["ytick.major.size"] = 2
    plt.rcParams["ytick.major.width"] = 0.4
    plt.rcParams["ytick.major.pad"] = 2
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.labelpad"] = 2

    results = {
        "Folder": [],
        "R2": [],
        "P_value": [],
        "intercept": [],
        "std_err": [],
    }

    subplot_len = int(len(sites) / 2)

    fig, axes = plt.subplots(
        subplot_len,
        2,
    )
    axes = axes.flatten()

    for site, ax in zip(sites, axes):
        canopy, slope, diff = slope_cc(site)

        # Perform linear regression
        slope_linreg, intercept, r_value, p_value, std_err = stats.linregress(
            canopy, diff
        )
        append_results(
            results,
            Folder=site,
            R2=r_value,
            P_value=p_value,
            intercept=intercept,
            std_err=std_err,
        )

        # Calculate the regression line
        line = slope_linreg * canopy + intercept

        # Plot the data
        ax.scatter(canopy, diff, label="Data", alpha=0.4, color=folder_colour(site))
        ax.plot(
            canopy,
            line,
            color="red",
            label=f"Linear fit: y={slope_linreg:.2f}x + {intercept:.2f}",
        )

        # Add title and labels
        ax.set_title(f"{site} (R²={r_value**2:.2f}, p={p_value:.2e})")
        ax.set_xlabel("Canopy Cover")
        ax.set_ylabel("Elevation error (m)")
        ax.set_ylim(-40, 40)  #
        ax.set_xlim(0, 1)  #
        # ax.legend()

    # Adjust layout and show plot
    plt.tight_layout()
    plt.savefig(f"figures/canopy_regress.png")
    plt.clf()

    # save results to new csv
    resultsDf = pd.DataFrame(results)
    outCsv = f"data/canopy_regress.csv"
    resultsDf.to_csv(outCsv, index=False)
    print("Results written to: ", outCsv)


if __name__ == "__main__":
    t = time.perf_counter()
    cmdargs = analysisCommands()
    site = cmdargs.studyArea

    if site == "all":
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nouragues",
            # "oak_ridge",
            "paracou",
            "robson_creek",
            # "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        plot_matrix(study_sites)

    else:
        plot_matrix([site])

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
