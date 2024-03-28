from matplotlib import pyplot as plt
import pandas as pd


######################################

if __name__ == "__main__":
    """Main block"""
    # Relative path to filename from OOSA-code-public folder
    filename = "data/plots.gediWave.321262.666327.csv"

    # Read data in to RAM
    data = pd.read_csv(filename)
    print(data)
    data_filtered = data[data["wave"] > 0]
    print(data_filtered)

    # Sort by the time column
    # sortedData = data.sort_values("time").reset_index(drop=True)

    # Print out the columns
    # print(sortedData.columns)

    # Mean of a column
    # print("mean time", sortedData["time"].mean())

    # Bounds
    # print("x bounds", sortedData["lon"].min(), sortedData["lat"].max())
    # print(min(data["wave"]))

    plt.plot(data_filtered["wave"], data_filtered["z"], color="green")
    # plt.ylim(200, None)
    plt.ylabel("Elevation (m)")
    plt.xlabel("DN")
    plt.title("Waveform with 0 wave values filtered out")
    plt.show()
