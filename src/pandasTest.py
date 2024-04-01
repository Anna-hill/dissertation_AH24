from matplotlib import pyplot as plt
import pandas as pd


def metric_text(text_file, filename):

    # read GEDI_metric text file output
    df = pd.read_csv(text_file, delimiter=" ", header=0)

    for index, row in df.iterrows():
        true_height = row.iloc[1]

        # height calculated by gedi processing
        gedi_height = row.iloc[5]
        print(true_height, "TH", gedi_height, "GH", index)

    # plot csv of wave
    data = pd.read_csv(filename)
    data_filtered = data[data["wave"] > 0]
    plt.plot(data_filtered["wave"], data_filtered["z"], color="green")
    plt.axhline(gedi_height, color="red", label="GEDI ground")
    plt.axhline(true_height, color="black", label="True ground")
    plt.legend()
    plt.ylabel("Elevation (m)")
    plt.xlabel("DN")
    # plt.title("Waveform with 0 wave values filtered out")
    plt.savefig("Plot.321262.666327.png")
    plt.clf()


######################################

if __name__ == "__main__":
    """Main block"""

    # read files
    filename = "data/plots.gediWave.321262.666327.csv"
    text_file = "data/wave_metrics.txt"
    metric_text(text_file, filename)
