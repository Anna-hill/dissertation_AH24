import pandas as pd

if __name__ == "__main__":

    df = pd.read_csv("data/teastMetric.metric.txt", delimiter=" ", header=0)

    for index, row in df.iterrows():
        true_height = row.iloc[1]

        # height calculated by gedi processing
        gedi_height = row.iloc[5]
        print(true_height, "TH", gedi_height, "GH")

    # print(true_height)
    # header is a bit messy, so difficult to just pull out lon/lat
