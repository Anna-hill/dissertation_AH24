import time
import argparse
from matplotlib import pyplot as plt
import pandas as pd


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
        "--plottype",
        dest="plotTyple",
        type=int,
        default="1",
        help=("Type of plot to produce"),
    )

    cmdargs = p.parse_args()
    return cmdargs


def read_csv(filename):
    data = pd.read_csv(filename, delimiter=",", header=0)
    # better way to filter?
    data_filtered = data[data["RMSE"] <= 3]
    data_filtered = data_filtered[data_filtered["Noise"] < 104]
    plt.scatter(
        data_filtered["Mean_Canopy_cover"], data_filtered["Noise"], color="green"
    )
    plt.ylabel("Noise (photons)")
    plt.xlabel("Mean canopy cover")
    plt.show()
    return data


def read_csv2(filename):
    data = pd.read_csv(filename, delimiter=",", header=0)
    data_filtered = data[data["Noise"] < 104]
    # data_filtered = data[data["RMSE"] <= 3]
    plt.scatter(data_filtered["Mean_Canopy_cover"], data_filtered["RMSE"])
    plt.xlabel("Mean canopy cover")
    plt.ylabel("RMSE")
    plt.show()
    return data


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = analysisCommands()
    results_csv = cmdargs.inFile

    read_csv2(results_csv)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
