import time
import argparse
import numpy as np
from matplotlib import pyplot as plt
from glob import glob
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression


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

    cmdargs = p.parse_args()
    return cmdargs


def filePath(folder, date):
    """Function to test file paths and glob"""

    file = f"data/{folder}"

    file_list = glob(file + f"/summary_stats_{folder}_{date}.csv")
    return file_list


def read_csv(folder, date):
    # csv file iterations are named by date (format DDMM)
    csv_file = filePath(folder, date)
    df = pd.read_csv(csv_file[0], delimiter=",", header=0)

    # find proportion of data pixels to no_data
    df["data_prop"] = (df["Data_count"] - df["NoData_count"]) / df["Data_count"]

    # Filter out rows where the proportion of valid pixels is over 50%
    filtered_df = df[df["data_prop"] >= 0.5]
    # better way to filter?
    df_folder = filtered_df.groupby(["nPhotons", "Noise"])

    # grouped = data.groupby(['photons', 'noise'])

    for (photons, noise), group in df_folder:

        # Bin values by mean cc (as percentage)
        bin_size = 2
        bins = np.arange(0, 101, bin_size)
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
        # Ignore N, P combos without any 3 < rmse
        if np.any(mean_rmse <= 3):
            # Plot the boxplots using seaborn
            plt.figure(figsize=(15, 8))
            # Add a horizontal dashed line at rmse=3
            plt.axhline(y=3, color="grey", linestyle="--", linewidth=1)
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
            plt.title(f"RMSE for Photons: {photons} and Noise: {noise}")

            plt.savefig(f"figures/box_plots/{folder}/box_p{photons}_n{noise}.png")
            plt.close()
        else:
            print(f"RMSE for Photons: {photons} and Noise: {noise} not below 3")

            # plot box plot function
            # print(df_folder.get_group(["500"]))
        # df_filtered = df[df["RMSE"] <= 3]
        # df_filtered = df_filtered[df_filtered["Noise"] < 104]
        # plt.scatter(df_filtered["Mean_Canopy_cover"], df_filtered["Noise"], color="green")
        # plt.ylabel("Noise (photons)")
        # plt.xlabel("Mean canopy cover")
        # plt.show()
    return df


def read_csv2(filename):
    df = pd.read_csv(filename, delimiter=",", header=0)
    df_filtered = df[df["Noise"] < 104]
    df_folder = df.groupby(["Folder", "Noise"])  # can group by multiple things
    print(df_folder.get_group(["wind_river"], [4]))
    # df_filtered = df[df["RMSE"] <= 3]
    plt.scatter(df_filtered["Mean_Canopy_cover"], df_filtered["RMSE"])
    plt.xlabel("Mean canopy cover")
    plt.ylabel("RMSE")
    plt.show()
    return df


def summary_scatter(date):
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
        csv = filePath(site, date)
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
        plt.title(f"Error for Photons: {photons} and Noise: {noise}")
        plt.xlabel("Canopy cover")
        plt.ylabel("RMSE")
        plt.legend(title="Study Area")
        plt.show()


# canopy as pc
# group by canopy (1 pc)
# mean rmse per canopy
# make boxplot of rmse/canopy cover
# find beam sensitivity
# add vertical line at bs point
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.boxplot.html

# shell function to interpret plot type inputs if too many?

if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = analysisCommands()
    results_csv = cmdargs.inFile
    site = cmdargs.studyArea
    # set csv date as arg? or produce consistant csv names

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
            # read_csv2(area)
            read_csv(area, "3006")
    else:
        # read_csv2(site)
        read_csv(site, "3006")

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")

    """import matplotlib.pyplot as plt
    import numpy as np

    np.random.seed(19680801)
    fruit_weights = [
        np.random.normal(130, 10, size=100),
        np.random.normal(125, 20, size=100),
        np.random.normal(120, 30, size=100),
    ]
    labels = ['peaches', 'oranges', 'tomatoes']
    colors = ['peachpuff', 'orange', 'tomato']

    fig, ax = plt.subplots()
    ax.set_ylabel('fruit weight (g)')

    bplot = ax.boxplot(fruit_weights,
                    patch_artist=True,  # fill with color
                    tick_labels=labels)  # will be used to label x-ticks

    # fill with colors
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    plt.show()"""
