import time
import rasterio
import numpy as np
from matplotlib import pyplot as plt
from glob import glob
import pandas as pd
from scipy import stats, optimize
import mpl_scatter_density
from scipy.stats import gaussian_kde
from matplotlib.animation import FuncAnimation
from lasBounds import append_results
from plotting import folder_colour
from analyseResults import analysisCommands


def find_merged(folder):
    file_path = f"data/{folder}/merged_rasters"
    # data/Bonaly/merged_rasters/b_p149_n15_diff_linear.tif

    canopy_list = glob(file_path + f"/*canopy.tif")
    slope_list = glob(file_path + f"/*slope.tif")
    diff_l_list = glob(file_path + f"/*diff_linear.tif")
    diff_c_list = glob(file_path + f"/*diff_cubic.tif")
    print("reading files :", canopy_list, slope_list, diff_l_list, diff_c_list)
    return canopy_list[0], slope_list[0], diff_l_list[0], diff_c_list[0]


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

    canopy_tif, slope_tif, diff_l_tif, diff_c_tif = find_merged(folder)

    read_canopy = open_raster(canopy_tif)
    read_slope = open_raster(slope_tif)
    read_l_diff = open_raster(diff_l_tif)
    read_c_diff = open_raster(diff_c_tif)

    # find max array dims
    max_shape = (
        max(
            read_canopy.shape[0],
            read_slope.shape[0],
            read_l_diff.shape[0],
            read_c_diff.shape[0],
        ),
        max(
            read_canopy.shape[1],
            read_slope.shape[1],
            read_l_diff.shape[1],
            read_c_diff.shape[1],
        ),
    )

    # Resize arrays to the maximum shape
    canopy_padded = pad_array(read_canopy, max_shape)
    slope_padded = pad_array(read_slope, max_shape)
    diff_l_padded = pad_array(read_l_diff, max_shape)
    diff_c_padded = pad_array(read_c_diff, max_shape)

    # remove 0 values and ensure same raster dims
    """combined_mask = (canopy_padded > 0) and (slope_padded > 0) and (diff_padded != 0)
    masked_canopy = np.where(combined_mask, canopy_padded, np.nan)
    masked_slope = np.where(combined_mask, slope_padded, np.nan)
    masked_diff = np.where(combined_mask, diff_padded, np.nan)"""

    # print(masked_canopy.shape, masked_slope.shape, masked_diff.shape)

    # flatten arrays for stats
    flat_canopy = canopy_padded.flatten()
    flat_slope = slope_padded.flatten()
    flat_l_diff = diff_l_padded.flatten()
    flat_c_diff = diff_c_padded.flatten()

    # convert all negative vals to pos for abs error
    # flat_diff = np.where(flat_diff < 0, -flat_diff, flat_diff)

    # append arrays into df
    """merged_rasters = {
        "canopy": [],
        "slope": [],
        "linear_difference": [],
        "cubic_difference": [],
    }
    append_results(
        merged_rasters,
        canopy=flat_canopy,
        slope=flat_slope,
        linear_difference=flat_l_diff,
        cubic_difference=flat_c_diff,
    )
    merged_rasters_df = pd.DataFrame(merged_rasters)"""
    all_arrays = np.vstack([flat_canopy, flat_slope, flat_l_diff, flat_c_diff])

    return all_arrays


def plot_matrix(sites, plot_data):

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.figsize"] = (8, 12)
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
        "slope": [],
    }

    subplot_len = int(len(sites) / 2)

    fig, axes = plt.subplots(subplot_len, 2)
    axes = axes.flatten()

    for site, ax in zip(sites, axes):
        all_arrays = slope_cc(site)
        print(f"raster values for {site}")
        print(all_arrays[0])

        # If type == 1
        if plot_data == 1:
            # return df error (linear) as var y, and slope as var x
            var_x = all_arrays[1]
            var_y = abs(all_arrays[2])

            # filter out 0 values
            non_zero_mask = (
                (var_x != 0) & (var_y != 0) & (var_y <= 50)
            )  # Oak ridge has an outlier pixel at 100m error

            # only slope values within given cc range
            range_mask = (all_arrays[0] >= 0.9) & (all_arrays[0] <= 0.95)

            # Combine the masks
            combined_mask = non_zero_mask & range_mask

            # Apply the mask to filter the arrays
            var_x = var_x[combined_mask]
            var_y = var_y[combined_mask]
            bs_limit = 4

            axis_x = "Slope (°)"
            axis_y = "Absolute elevation error (m)"
            outname = "slope"

        elif plot_data == 2:
            # return df error (linear) as var y, and CC as var x
            var_x = all_arrays[0]
            var_y = abs(all_arrays[2])

            # filter out 0 values
            non_zero_mask = (
                (var_x != 0) & (var_y != 0) & (var_y <= 50)
            )  # Oak ridge has an outlier pixel at 100m error

            # only cc values within given slope range
            range_mask = (all_arrays[1] >= 10) & (all_arrays[1] <= 15)

            # Combine the masks
            combined_mask = non_zero_mask & range_mask

            # Apply the mask to filter the arrays
            var_x = var_x[combined_mask]
            var_x = var_x * 100
            var_y = var_y[combined_mask]
            bs_limit = 4

            axis_x = "Canopy Cover (%)"
            axis_y = "Absolute elevation error (m)"
            outname = "canopy"

        else:
            # return df error (linear) as var y, and error (cubic) as var x
            var_x = all_arrays[3]
            var_y = all_arrays[2]

            bs_limit = 0

            # filter out 0 values
            non_zero_mask = (
                (var_x != 0) & (var_y != 0) & (abs(var_y) <= 50) & (abs(var_x) <= 50)
            )  # Oak ridge has one outlier pixel at 100m error

            var_y = abs(var_y[non_zero_mask])
            var_x = abs(var_x[non_zero_mask])

            lims = (min(min(var_x), min(var_y)), max(max(var_x), max(var_y)))

            axis_x = "cubic elevation error (m)"
            axis_y = "Linear elevation error (m)"
            outname = "interpolation"

        # Descriptive statistics?
        # print(stats.describe(var_x))
        # print(stats.describe(var_y))

        slope_linreg, intercept, r_value, p_value, std_err = stats.linregress(
            var_x,
            var_y,
        )
        append_results(
            results,
            Folder=site,
            R2=(r_value**2),
            P_value=p_value,
            intercept=intercept,
            std_err=std_err,
            slope=slope_linreg,
        )

        # point density solution from https://stackoverflow.com/questions/20105364/how-can-i-make-a-scatter-plot-colored-by-density
        # Calculate the point density
        xy = np.vstack([var_x, var_y])
        z = gaussian_kde(xy)(xy)

        # Sort the points by density, so that the densest points are plotted last
        idx = z.argsort()
        x, y, z = var_x[idx], var_y[idx], z[idx]

        # ax = fig.add_subplot(1, 1, 1, projection="scatter_density")
        # density = ax.scatter_density(var_x, var_y, cmap="viridis")
        # fig.colorbar(density, label="Number of points per pixel")

        # Plot the data
        ax.scatter(x, y, c=z, s=5)
        ax.axhline(y=bs_limit, color="grey", linestyle="--", linewidth=1)

        # Add title and labels
        ax.set_title(f"{site} (R²={r_value**2:.2f}, p={p_value:.2e})")
        ax.set_xlabel(axis_x)
        ax.set_ylabel(axis_y)
        if plot_data == 3:
            # ensure diff interpolation models have same x y lims
            ax.set_ylim(lims)  #
            ax.set_xlim(lims)  #

    # Adjust layout and show plot
    plt.tight_layout()
    plt.savefig(f"figures/{outname}_regress.png")
    plt.clf()

    # save results to new csv
    resultsDf = pd.DataFrame(results)
    outCsv = f"data/{outname}_regress.csv"
    resultsDf.to_csv(outCsv, index=False)
    print("Results written to: ", outCsv)

    return all_arrays

    ###########


def plot3D(merged_array, site):

    # set plot settings
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.figsize"] = (8, 6)
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["xtick.major.size"] = 2
    plt.rcParams["xtick.major.width"] = 0.4
    plt.rcParams["xtick.major.pad"] = 2
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["ytick.major.size"] = 2
    plt.rcParams["ytick.major.width"] = 0.4
    plt.rcParams["ytick.major.pad"] = 2
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.labelpad"] = 3
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["lines.linewidth"] = 1
    plt.rcParams["lines.markersize"] = 4

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    X = merged_array[0] * 100  # canopy
    Y = merged_array[1]  # slope
    Z = abs(merged_array[2])  # error
    scat = ax.scatter(X, Y, Z, c=Z, cmap="viridis", alpha=0.4)

    # Add a color bar to indicate the scale of Z values
    color_bar = plt.colorbar(scat, ax=ax, pad=0.1)
    color_bar.set_label("Absolute elevation error (m)")

    ax.set_xlabel("Canopy cover (%)")
    ax.set_ylabel("Slope (°)")
    ax.set_zlabel("Absolute elevation error (m)")

    plt.title(f"{site}")

    # create static image
    fig.savefig(f"figures/scatter_plots/{site}_error_controls.png")

    # Function to update the view angle
    def update(frame):
        ax.view_init(elev=30, azim=frame)
        return (scat,)

    # Create an animation
    ani = FuncAnimation(
        fig, update, frames=np.arange(0, 360, 1), interval=50, blit=True
    )

    # Save the animation as a GIF
    outname = f"figures/scatter_plots/rotating_{site}.gif"
    ani.save(outname, writer="imagemagick")
    print(f"Gif saved to {outname}")


if __name__ == "__main__":
    t = time.perf_counter()
    cmdargs = analysisCommands()
    site = cmdargs.studyArea
    plot_type = cmdargs.plotType
    # types:
    # 1 = Slope
    # 2 = Canopy
    # 3 = Interpolation method

    if site == "all":
        study_sites = [
            # "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nouragues",
            "oak_ridge",
            "paracou",
            "robson_creek",
            # "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        plot_matrix(study_sites, plot_type)
        for site_x in study_sites:
            results_array = slope_cc(site_x)
            # plot3D(results_array, site_x)

    else:
        results_array = plot_matrix([site], plot_type)
        results_array = slope_cc(site)
        # plot3D(results_array, site)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
