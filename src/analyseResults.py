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
from plotting import three_D_scatter
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
    cmdargs = p.parse_args()
    return cmdargs


def filePath(folder, las_settings, interpolation):
    """Function to test file paths and glob"""

    file = f"data/{folder}"

    file_list = glob(file + f"/summary_{folder}_{las_settings}{interpolation}.csv")
    return file_list


def read_csv(folder, las_settings, interpolation):
    # csv file iterations are named by las_settings
    csv_file = filePath(folder, las_settings, interpolation)
    df = pd.read_csv(csv_file[0], delimiter=",", header=0)

    # either justify, or negate by interpolating
    """# find proportion of data pixels to no_data
    df["data_prop"] = (df["Data_count"] - df["NoData_count"]) / df["Data_count"]

    # Filter out rows where the proportion of valid pixels is over 50%
    filtered_df = df[df["data_prop"] >= 0.5]"""
    filtered_df = df[df["RMSE"] != -999.0]
    df_folder = filtered_df.groupby(["nPhotons", "Noise"])

    results = {
        "Folder": [],
        "nPhotons": [],
        "Noise": [],
        "RMSE": [],
        "Bias": [],
        "beam_sensitivity": [],
    }

    for (photons, noise), group in df_folder:

        # beam sensitivity?
        # print(group["RMSE"] > 3.0["Mean_Canopy_cover"].min)

        # Bin values by mean cc (as percentage)
        bin_size = 1
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

        # Find mean values
        mean_rmse = group.groupby("CC_bin")["RMSE"].mean().values

        # Ignore N, P combos without any 4 < rmse
        if np.any(mean_rmse <= 4):
            if np.all(group["RMSE"] <= 4):
                beam_sens = 1
            else:
                beam_sens = group[group["RMSE"] > 4]["Mean_Canopy_cover"].min()

            rmse_mean = np.mean(group["RMSE"])
            bias_mean = np.mean(group["Bias"])

            append_results(
                results,
                Folder=folder,
                nPhotons=photons,
                Noise=noise,
                beam_sensitivity=beam_sens,
                RMSE=rmse_mean,
                Bias=bias_mean,
            )
            # Plot the boxplots using seaborn
            plt.figure(figsize=(15, 8))
            # Add a horizontal dashed line at rmse=3
            plt.axhline(y=4, color="grey", linestyle="--", linewidth=1)
            # plt.axvline(x=(beam_sens * 100), color="red", linestyle="--", linewidth=1)
            sns.boxplot(
                x="CC_bin",
                y="RMSE",
                data=group,
                whis=[0, 100],
                width=0.6,
            )
            # Fit a line of best fit to the mean rmse values (make function???)
            x = np.arange(len(bin_labels)).reshape(-1, 1)
            y = mean_rmse

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
            )

            # Plot a line joining all the mean values of rmse for each bin
            # very disjointed and hard to understand. revisit when more data points
            """plt.plot(
                np.arange(len(bin_labels)),
                mean_rmse,
                # marker="o",
                color="r",
                label="Mean RMSE",
            )"""

            # Set x-axis tick labels
            plt.xticks(ticks=np.arange(len(bin_labels)), labels=bin_labels, rotation=90)

            # Set y-axis range
            # plt.ylim(0, 50)
            # set labels and title
            plt.xlabel("Mean Canopy cover (%)")
            plt.ylabel("RMSE (m)")
            plt.title(
                f"RMSE for Photons: {photons} and Noise: {noise} (las settings={las_settings})"
            )

            plt.savefig(
                f"figures/box_plots/{folder}/box_p{photons}_n{noise}_{las_settings}.png"
            )
            plt.close()
        else:
            print(
                f"RMSE for {folder} Photons: {photons} and Noise: {noise} not below 4"
            )
    # save results to new csv
    resultsDf = pd.DataFrame(results)
    outCsv = f"data/beam_sensitivity/{las_settings}/{folder}.csv"
    resultsDf.to_csv(outCsv, index=False)
    print("Results written to: ", outCsv)
    return outCsv


def summary_scatter(las_settings):
    """Scatter plots combining all sites"""
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
    csv_list = []
    for site in study_sites:
        csv = filePath(site, las_settings)
        csv_list.append(csv[0])
    # print(csv_list)
    dfs = [pd.read_csv(file) for file in csv_list]

    # Concatenate all DataFrames into one
    df = pd.concat(dfs, ignore_index=True)

    # find proportion of data pixels to no_data
    df["data_prop"] = (df["Data_count"] - df["NoData_count"]) / df["Data_count"]

    # Filter out rows where the proportion of valid pixels is over 50%
    filtered_df = df[df["data_prop"] >= 0.5]
    print(filtered_df)

    # group into n p combinations
    df_folder = filtered_df.groupby(["nPhotons", "Noise"])

    # check examples for other ways to do this
    color_map = {
        site: color
        for site, color in zip(
            filtered_df["Folder"].unique(), plt.cm.get_cmap("Dark2").colors
        )
    }

    for (photons, noise), group in df_folder:
        plt.figure()
        for site in group["Folder"].unique():
            site_group = group[group["Folder"] == site]
            plt.scatter(
                site_group["Mean_Canopy_cover"],
                site_group["RMSE"],
                color=color_map[site],
                label=site,
            )
        plt.title(f"Error for Photons: {photons} and Noise: {noise} ({las_settings})")
        plt.xlabel("Canopy cover")
        plt.ylabel("RMSE")
        plt.legend(title="Study Area")
        plt.show()


def concat_csv(csv_list, las_settings):

    # file path function
    file_path = f"data/beam_sensitivity/{las_settings}"
    # csv_list = glob(file_path + "/*.csv")

    # for csv in file_list:
    #  csv_list.append(csv[0])
    # print(csv_list)
    dfs = [pd.read_csv(file) for file in csv_list]

    # Concatenate all DataFrames into one
    df = pd.concat(dfs, ignore_index=True)

    # make 3d plot of photon, noise, bs (folder as colour?)
    # Most high noise vals removed in prev function
    # three_D_scatter(df["nPhotons"], df["Noise"], df["beam_sensitivity"], df["Folder"], las_settings)
    outCsv = f"{file_path}/summary_stats.csv"
    print(f"file saved to: {outCsv}")
    df.to_csv(outCsv, index=False)
    return df


def plot3D(df):

    # set colour scheme
    color_map = {
        site: color
        for site, color in zip(df["Folder"].unique(), plt.cm.get_cmap("Dark2").colors)
    }

    fig = plt.figure(figsize=(15, 8))
    ax = fig.add_subplot(projection="3d")

    # ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)

    for site in df["Folder"].unique():
        site_group = df[df["Folder"] == site]
        X = site_group["nPhotons"]
        Y = site_group["Noise"]
        Z = site_group["beam_sensitivity"]
        scat = ax.scatter(X, Y, Z, color=color_map[site], label=site)
    ax.set_xlabel("Photons")
    ax.set_ylabel("Noise")
    ax.set_zlabel("Beam Sensitivity")
    ax.legend(loc="upper left")

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


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = analysisCommands()
    results_csv = cmdargs.inFile
    site = cmdargs.studyArea
    las_settings = cmdargs.lasSettings
    intp_setting = cmdargs.intpSettings

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
            "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for area in study_sites:
            csv_paths.append(read_csv(area, las_settings, intp_setting))

        # merge bs results into one file
        df = concat_csv(csv_paths, las_settings)

    else:
        read_csv(site, las_settings, intp_setting)

    # Make rotating 3D plot - saves as gif but very slow
    # set colours and font (rc params?)
    ##plot3D(df)
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
