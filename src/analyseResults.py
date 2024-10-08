import time
import argparse
import numpy as np
from matplotlib import pyplot as plt
from glob import glob
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from lasBounds import append_results
from plotting import folder_colour
from matplotlib.animation import FuncAnimation


def analysisCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(description=("Script to examine results of dtmShell"))

    p.add_argument(
        "--studyarea",
        dest="studyArea",
        type=str,
        default="Bonaly",
        help=("Study area name"),
    )

    p.add_argument(
        "--plottype",
        dest="plotType",
        type=int,
        default="1",
        help=("Type of plot to produce"),
    )
    p.add_argument(
        "--lassettings",
        dest="lasSettings",
        type=str,
        default="400505",
        help=("Choose input based on lastools settings applied to find gound"),
    )

    p.add_argument(
        "--interpolation",
        dest="intpSettings",
        type=str,
        default="",
        help=("Choose input based on interpolation settings"),
    )
    p.add_argument(
        "--bs_thresh",
        dest="bs_thresh",
        type=float,
        default=4,
        help=("Beam sensitivty threshold"),
    )
    p.add_argument(
        "--outliers",
        dest="bs_outlier",
        type=int,
        default=1,
        help=("Whether to include RMSE values in upper quantile of cc bin in bs calc"),
    )
    cmdargs = p.parse_args()
    return cmdargs


def filePath(folder, las_settings, interpolation):
    """Function to find file paths with glob"""

    file = f"data/{folder}"

    file_list = glob(file + f"/summary_{folder}_{las_settings}{interpolation}.csv")
    return file_list


def read_csv(folder, las_settings, interpolation, bs_limit, tf_outliers, study_sites):
    """Read results of dtmShell from CSV, group model performace by processing settings, calculate beam sensitivty and make plots

    Args:
        folder (str): study site
        las_settings (str): lassettings used
        interpolation (str): interpolation method used
        bs_limit (int): threshold for beam sensitivty calculations
        tf_outliers (int): include outliers in box plot (1) or not (0)
        study_sites (lits):list of site names

    Returns:
        str: name of output csv file
    """

    if folder == "all":
        # read all appropriate dataframes and join into 1
        csv_list = []
        for site in study_sites:
            csv_list.append((filePath(site, las_settings, interpolation))[0])
        dfs = [pd.read_csv(file) for file in csv_list]
        df = pd.concat(dfs, ignore_index=True)

    else:
        # csv file iterations are named by las_settings
        csv_file = filePath(folder, las_settings, interpolation)
        # new line to read concat csv?
        df = pd.read_csv(csv_file[0], delimiter=",", header=0)

    # remove no data rows
    filtered_df = df[df["RMSE"] != -999.0]

    # group by processing settings
    df_p_n = filtered_df.groupby(["nPhotons", "Noise"])

    results = {
        "Folder": [],
        "las_settings": [],
        "nPhotons": [],
        "Noise": [],
        "RMSE": [],
        "Bias": [],
        "Pixel_count": [],
        "nodata_count": [],
        "nodata_prop": [],
        "beam_sensitivity": [],
    }

    for (photons, noise), group in df_p_n:
        sum_pixels = sum(group["Data_count"])
        sum_nodata = sum(group["NoData_count"])

        # Bin values by mean cc (as percentage)
        bin_size = 2
        bins = np.arange(0, 101, bin_size)

        # bin data by mean canopy cover
        group["CC_bin"] = pd.cut(
            (group["Mean_Canopy_cover"] * 100),
            bins=bins,
            include_lowest=True,
            right=False,
        )
        # Set bin labels as single number as more readable
        bin_labels = [f"{b+bin_size}" for b in bins[:-1]]

        # Filter out bins with fewer than 2 values
        bin_counts = group["CC_bin"].value_counts()
        valid_bins = bin_counts[bin_counts >= 2].index
        group = group[group["CC_bin"].isin(valid_bins)]

        if group.empty:
            print(f"Not enough data to plot for Photons: {photons}, Noise: {noise}")
            continue

        # Find mean values
        mean_rmse = group.groupby("CC_bin")["RMSE"].mean().values

        # Ignore N, P combos without any bs_thresh < rmse
        if np.any(mean_rmse <= bs_limit):
            if tf_outliers == 1:
                if np.all(group["RMSE"] <= bs_limit):
                    beam_sens = 1
                else:
                    # beam sens on all rmse, not mean bin?
                    beam_sens = group[group["RMSE"] > bs_limit][
                        "Mean_Canopy_cover"
                    ].min()

            # calculate beam sensitivity from RMSE values within lower 3 quartiles of CC bins
            elif tf_outliers == 0:
                # Define upper quantile threshold
                upper_quantile = 0.75
                # Calculate the RMSE value at the upper quantile
                upper_quantile_threshold = group["RMSE"].quantile(upper_quantile)

                # Filter RMSE values below the upper quantile threshold and above the bs_limit
                filtered_rmse = group[group["RMSE"] <= upper_quantile_threshold]
                beam_sens = filtered_rmse[filtered_rmse["RMSE"] > bs_limit][
                    "Mean_Canopy_cover"
                ].min()
                if np.all(filtered_rmse["RMSE"] <= bs_limit):
                    beam_sens = 1
                else:
                    # Calculate the minimum canopy cover for the filtered RMSE values
                    beam_sens = filtered_rmse["Mean_Canopy_cover"].min()
                    print("beam sens", beam_sens)

            rmse_mean = np.mean(group["RMSE"])
            bias_mean = np.mean(group["Bias"])

            # set plot settings
            plt.rcParams["font.family"] = "Times New Roman"
            plt.rcParams["figure.constrained_layout.use"] = True
            plt.rcParams["figure.figsize"] = (8, 5)
            plt.rcParams["xtick.labelsize"] = 8
            plt.rcParams["xtick.major.size"] = 2
            plt.rcParams["xtick.major.width"] = 0.4
            plt.rcParams["xtick.major.pad"] = 2
            plt.rcParams["ytick.labelsize"] = 8
            plt.rcParams["ytick.major.size"] = 2
            plt.rcParams["ytick.major.width"] = 0.4
            plt.rcParams["ytick.major.pad"] = 2
            plt.rcParams["axes.labelsize"] = 10
            plt.rcParams["axes.linewidth"] = 0.5
            plt.rcParams["axes.labelpad"] = 3
            plt.rcParams["axes.titlesize"] = 12
            plt.rcParams["lines.linewidth"] = 1
            plt.rcParams["lines.markersize"] = 4
            plt.rcParams["legend.frameon"] = False

            # Plot the boxplots using seaborn
            plt.figure()

            # Add a horizontal dashed line at rmse=3
            plt.axhline(y=bs_limit, color="grey", linestyle="--", linewidth=1)

            sns.boxplot(
                x="CC_bin",
                y="RMSE",
                data=group,
                whis=[0, 100],
                width=0.6,
                color=folder_colour(folder),
            )

            # Fit a line of best fit to the mean rmse values
            x = np.arange(len(bin_labels)).reshape(-1, 1)
            y = mean_rmse

            # Filter out NaN values
            mask = ~np.isnan(y)

            # fit linear relationship to data
            x_filtered = x[mask].reshape(-1, 1)
            y_filtered = y[mask]
            model = LinearRegression()
            model.fit(x_filtered, y_filtered)
            y_pred = model.predict(x_filtered)

            # Plot the line of best fit
            plt.plot(
                x_filtered,
                y_pred,
                color="red",
                linestyle=":",
                label="line of best fit for mean RMSE",
            )

            plt.text(
                x=1,
                y=2,
                s=f"Beam sensitivity: {beam_sens * 100:.2f}%",
                horizontalalignment="left",
                verticalalignment="top",
            )

            # Set x-axis tick labels
            plt.xticks(ticks=np.arange(len(bin_labels)), labels=bin_labels, rotation=90)

            # set labels and title
            plt.xlabel("Mean Canopy cover (%)")
            plt.ylabel("RMSE (m)")
            plt.legend(loc="upper left")
            plt.title(
                f"{folder}: {photons} photons and {noise} noise with las settings {las_settings}"
            )

            plt.savefig(
                f"figures/box_plots/{folder}/bs{bs_limit}_p{photons}_n{noise}_{las_settings}_o{tf_outliers}.png"
            )
            plt.close()

            append_results(
                results,
                Folder=folder,
                las_settings=las_settings,
                nPhotons=photons,
                Noise=noise,
                beam_sensitivity=beam_sens,
                RMSE=rmse_mean,
                Bias=bias_mean,
                Pixel_count=sum_pixels,
                nodata_count=sum_nodata,
                nodata_prop=(sum_nodata / sum_pixels) * 100,
            )

        else:
            print(
                f"RMSE for {folder} Photons: {photons} and Noise: {noise} not below 4"
            )
    # save results to new csv
    resultsDf = pd.DataFrame(results)
    outCsv = (
        f"data/beam_sensitivity/{las_settings}/{folder}_bs{bs_limit}_o{tf_outliers}.csv"
    )
    resultsDf.to_csv(outCsv, index=False)
    print("Results written to: ", outCsv)
    return outCsv


def concat_csv(csv_list, las_settings):
    """Join multiple csv files into one dataframe

    Args:
        csv_list (list):  csv file names
        las_settings (str): lassettigns code in file names

    Returns:
        dataframe: merged files as dataframe
    """

    # file path function
    file_path = f"data/beam_sensitivity/{las_settings}"

    dfs = [pd.read_csv(file) for file in csv_list]

    # Concatenate all DataFrames into one
    df = pd.concat(dfs, ignore_index=True)

    outCsv = f"{file_path}/summary_stats_bs{bs_limit}_o{tf_outliers}.csv"
    print(f"file saved to: {outCsv}")
    df.to_csv(outCsv, index=False)
    return df


def bs_subplots(df, bs_limit, tf_outliers):
    """Make line plots of beam sensitivty results agaisnt noise/photons

    Args:
        df (dataframe): beam sensitivity results
        bs_limit (int): bs threshold
        tf_outliers (int): outlier inclusion code
    """
    # filter out old results
    filtered_df = df[df["Noise"] != 5]
    filtered_df = filtered_df[filtered_df["nPhotons"] != 400]

    # Group the data by noise
    noise_groups = filtered_df.groupby("Noise")

    # Create subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6))
    axes = axes.flatten()

    # Iterate over each noise level and corresponding axis
    for (noise, group), ax in zip(noise_groups, axes):
        for folder in group["Folder"].unique():
            folder_data = group[group["Folder"] == folder]

            # convert dataframe rows to np arrays
            nPhotons = folder_data["nPhotons"].to_numpy()
            beam_sensitivity = folder_data["beam_sensitivity"].to_numpy()
            ax.plot(
                nPhotons,
                beam_sensitivity,
                marker="o",
                label=folder,
                color=folder_colour(folder),
            )
        ax.axhline(y=0.98, color="grey", linestyle="--", linewidth=1)
        ax.set_title(f"{noise} noise photons")
        ax.set_xlabel("Number of signal photons")
        ax.set_ylabel("Beam Sensitivity")
        ax.set_ylim(0, 1)

    labels_handles = {
        label: handle
        for ax in fig.axes
        for handle, label in zip(*ax.get_legend_handles_labels())
    }

    fig.legend(
        labels_handles.values(),
        labels_handles.keys(),
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        bbox_transform=plt.gcf().transFigure,
        borderaxespad=0.0,
    )

    outname = f"figures/line_plots/{las_settings}_bs{bs_limit}_o{tf_outliers}.png"
    fig.savefig(outname)
    print(f"Plot saved to saved to {outname}")
    plt.clf()


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = analysisCommands()
    site = cmdargs.studyArea
    las_settings = cmdargs.lasSettings
    intp_setting = cmdargs.intpSettings
    bs_limit = cmdargs.bs_thresh
    tf_outliers = cmdargs.bs_outlier

    csv_paths = []

    if site == "all":
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nouragues",
            "oak_ridge",
            "paracou",
            "robson_creek",
            "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for area in study_sites:
            csv_paths.append(
                read_csv(
                    area,
                    las_settings,
                    intp_setting,
                    bs_limit,
                    tf_outliers,
                    study_sites=study_sites,
                )
            )

        # merge bs results into one file
        df = concat_csv(csv_paths, las_settings)
        bs_subplots(df, bs_limit, tf_outliers)

        # all sites on one plot
        read_csv(
            folder="all",
            las_settings=las_settings,
            interpolation=intp_setting,
            bs_limit=bs_limit,
            tf_outliers=tf_outliers,
            study_sites=study_sites,
        )

    else:
        read_csv(
            site, las_settings, intp_setting, bs_limit, tf_outliers, study_sites=site
        )

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
