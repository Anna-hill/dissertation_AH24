from matplotlib import pyplot as plt
import pandas as pd


######################################

if __name__ == "__main__":
    """Main block"""
    # Relative path to filename from OOSA-code-public folder
    filename = "data/plots.gediWave.320752.665697.csv"

    # Read data in to RAM
    data = pd.read_csv(filename)
    print(data)

    # Sort by the time column
    # sortedData = data.sort_values("time").reset_index(drop=True)

    # Print out the columns
    # print(sortedData.columns)

    # Mean of a column
    # print("mean time", sortedData["time"].mean())

    # Bounds
    # print("x bounds", sortedData["lon"].min(), sortedData["lat"].max())

    plt.plot(
        data["wave"],
        data["z"],
    )
    plt.show()
