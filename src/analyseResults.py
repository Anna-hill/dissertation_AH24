import time
import argparse
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from glob import glob
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from lasBounds import append_results
from plotting import folder_colour
from matplotlib.animation import FuncAnimation

# more plots
# remove bins from plot where less than a number- justifyyyy???


def analysisCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(description=("Script to examine results of dtmShell"))

    p.add_argument(
        "--inFile",
        dest="inFile",
        type=str,
        default="data/results_all_3006.csv",
        help=("CSV file to analyse"),
    )
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
    cmdargs = p.parse_args()
    return cmdargs


def filePath(folder, las_settings, interpolation):
    """Function to test file paths and glob"""

    file = f"data/{folder}"

    file_list = glob(file + f"/summary_{folder}_{las_settings}{interpolation}.csv")
    return file_list


def read_csv(folder, las_settings, interpolation, bs_limit):
    # csv file iterations are named by las_settings
    csv_file = filePath(folder, las_settings, interpolation)
    df = pd.read_csv(csv_file[0], delimiter=",", header=0)

    # remove no data rows
    filtered_df = df[df["RMSE"] != -999.0]
    df_p_n = filtered_df.groupby(["nPhotons", "Noise"])

    results = {
        "Folder": [],
        "las_settings": [],
        "nPhotons": [],
        "Noise": [],
        "RMSE": [],
        "Bias": [],
        "beam_sensitivity": [],
    }

    for (photons, noise), group in df_p_n:

        # Bin values by mean cc (as percentage)
        bin_size = 2
        bins = np.arange(0, 101, bin_size)

        # if group < 1, filter out?
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

        # Ignore N, P combos without any bs thresh < rmse
        if np.any(mean_rmse <= bs_limit):
            if np.all(group["RMSE"] <= bs_limit):
                beam_sens = 1
            else:
                # beam sens on all rmse, not mean bin?
                beam_sens = group[group["RMSE"] > bs_limit]["Mean_Canopy_cover"].min()

            rmse_mean = np.mean(group["RMSE"])
            bias_mean = np.mean(group["Bias"])

            append_results(
                results,
                Folder=folder,
                las_settings=las_settings,
                nPhotons=photons,
                Noise=noise,
                beam_sensitivity=beam_sens,
                RMSE=rmse_mean,
                Bias=bias_mean,
            )

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

            # Plot the boxplots using seaborn
            plt.figure()
            # Add a horizontal dashed line at rmse=3
            plt.axhline(y=bs_limit, color="grey", linestyle="--", linewidth=1)
            # plt.axvline(x=(beam_sens * 100), color="red", linestyle="--", linewidth=1)
            sns.boxplot(
                x="CC_bin",
                y="RMSE",
                data=group,
                whis=[0, 100],
                width=0.6,
                color=folder_colour(folder),
            )

            # Fit a line of best fit to the mean rmse values (make function???)
            """x = np.arange(len(bin_labels)).reshape(-1, 1)
            y = mean_rmse

            # would cubic model fit better?
            # Filter out NaN values
            mask = ~np.isnan(y)
            x_filtered = x[mask].reshape(-1, 1)
            y_filtered = y[mask]
            model = LinearRegression()
            model.fit(x_filtered, y_filtered)
            y_pred = model.predict(x_filtered)

            # Plot the line of best fit
            plt.plot(
                x_filtered,
                y_pred,
                color="b",
                label="Mean RMSE (Line of Best Fit)",
            )"""

            # Set x-axis tick labels
            plt.xticks(ticks=np.arange(len(bin_labels)), labels=bin_labels, rotation=90)

            # set labels and title
            plt.xlabel("Mean Canopy cover (%)")
            plt.ylabel("RMSE (m)")
            plt.title(
                f"{folder}: {photons} photons and {noise} noise with las settings {las_settings}"
            )

            plt.savefig(
                f"figures/box_plots/{folder}/bs{bs_limit}_p{photons}_n{noise}_{las_settings}.png"
            )
            plt.close()
        else:
            print(
                f"RMSE for {folder} Photons: {photons} and Noise: {noise} not below 4"
            )
    # save results to new csv
    resultsDf = pd.DataFrame(results)
    outCsv = f"data/beam_sensitivity/{las_settings}/{folder}_bs{bs_limit}.csv"
    resultsDf.to_csv(outCsv, index=False)
    print("Results written to: ", outCsv)
    return outCsv


def concat_csv(csv_list, las_settings):

    # file path function
    file_path = f"data/beam_sensitivity/{las_settings}"

    dfs = [pd.read_csv(file) for file in csv_list]

    # Concatenate all DataFrames into one
    df = pd.concat(dfs, ignore_index=True)

    outCsv = f"{file_path}/summary_stats.csv"
    print(f"file saved to: {outCsv}")
    df.to_csv(outCsv, index=False)
    return df


def bs_subplots(df):
    # filter out old results
    filtered_df = df[df["Noise"] != 5]
    filtered_df = filtered_df[filtered_df["nPhotons"] != 400]

    # Group the data by Noise
    noise_groups = filtered_df.groupby("Noise")

    # Create subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 6))
    # fig.tight_layout(rect=(0, 0, 1, 0.9))
    axes = axes.flatten()  # Flatten the 2D array of axes to 1D for easy iteration

    # Iterate over each Noise level and corresponding axis
    for (noise, group), ax in zip(noise_groups, axes):
        for folder in group["Folder"].unique():
            folder_data = group[group["Folder"] == folder]

            # beter conversion
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

    # legend.get_frame().set_alpha(1)
    # legend.get_frame().set_facecolor("white")

    # Adjust the layout to make room for the legend
    # plt.subplots_adjust(right=0.85)
    # edit legend to only appear once, to the side
    # fig.legend(bbox_to_anchor=(1.05, 0), loc="lower left", borderaxespad=0.0)

    fig.savefig(f"figures/line_plots/{las_settings}.png")
    print(f"Plot saved to saved to f 'figures/line_plots/{las_settings}.png'")
    plt.clf()


def plot3D(df):

    # set plot settings
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.figsize"] = (8, 6)
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["legend.frameon"] = False
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

    for site in df["Folder"].unique():
        site_group = df[df["Folder"] == site]
        X = site_group["nPhotons"]
        Y = site_group["Noise"]
        Z = site_group["beam_sensitivity"]
        scat = ax.scatter(X, Y, Z, color=folder_colour(site), label=site)
    ax.set_xlabel("Photons")
    ax.set_ylabel("Noise")
    ax.set_zlabel("Beam Sensitivity")
    ax.legend(loc="upper left")

    plt.title(f"Beam Sensitivity for {las_settings} las settings")

    # create static image
    fig.savefig(f"figures/scatter_plots/{las_settings}.png")

    # Function to update the view angle
    def update(frame):
        ax.view_init(elev=30, azim=frame)
        return (scat,)

    # Create an animation
    ani = FuncAnimation(
        fig, update, frames=np.arange(0, 360, 1), interval=50, blit=True
    )

    # Save the animation as a GIF
    ani.save(f"figures/scatter_plots/rotating_{las_settings}.gif", writer="imagemagick")
    print(f"Gif saved to f 'figures/scatter_plots/rotating_{las_settings}.gif'")

    # close figure
    fig.close()


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = analysisCommands()
    results_csv = cmdargs.inFile
    site = cmdargs.studyArea
    las_settings = cmdargs.lasSettings
    intp_setting = cmdargs.intpSettings
    bs_limit = cmdargs.bs_thresh

    csv_paths = []

    # summary_scatter(3006)
    if site == "all":
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nouragues",
            "oak_ridge",
            "paracou",
            "robson_creek",
            # "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for area in study_sites:
            csv_paths.append(read_csv(area, las_settings, intp_setting, bs_limit))

        # merge bs results into one file
        df = concat_csv(csv_paths, las_settings)
        bs_subplots(df)
        # plot3D(df)

    else:
        read_csv(site, las_settings, intp_setting, bs_limit)

    # Make rotating 3D plot - saves as gif but very slow
    # set colours and font (rc params?)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
