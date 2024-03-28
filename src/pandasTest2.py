import pandas as pd

df = pd.read_csv("data/teastMetric.metric.txt", delimiter=" ")

print(df["lon,"])
# header is a bit messy, so difficult to just pull out lon/lat
