import pandas as pd
import numpy as np
import numpy.ma as ma
import rasterio
from rasterio.transform import from_origin
import re
import matplotlib.pyplot as plt
from plotting import one_plot


# Function to read the text file and extract data
def read_text_file(file_path):
    coordinates = []
    # xlist = []
    # ylist = []
    ground_values = []

    with open(file_path, "r") as file:
        lines = file.readlines()

        # Process lines one at a time
        for i in range(0, len(lines)):
            id_line = lines[i].strip()
            # ground_value_line = lines[i + 1].strip()
            # print(ground_value_line)

            # Extract coordinates from the ID line
            match = re.search(r"gediWave\.(\d+)\.(\d+)", id_line)
            if match:
                x, y = map(int, match.groups())
                # xlist.append(x)
                # ylist.append(y)
                coordinates.append([x, y])

                # Extract the ground value
                ground_value = float(id_line.split()[1])
                ground_values.append(ground_value)

    return coordinates, ground_values


# Function to create a TIFF file from the coordinates and ground values
def create_tiff(coordinates, ground_values, output_path, resolution=30):
    # Convert coordinates and ground values to numpy arrays
    # x_coord = np.array(x)
    # y_coord = np.array(y)
    coordinates = np.array(coordinates)
    # print(x_coord)
    ground_values = np.array(ground_values)
    # print(ground_values)

    # Determine the bounds of the raster
    min_x, min_y = coordinates.min(axis=0)
    max_x, max_y = coordinates.max(axis=0)

    # Determine the size of the raster
    width = (max_x - min_x) // resolution + 1
    height = (max_y - min_y) // resolution + 1

    # Create an empty array for the raster data
    raster_data = np.full((height, width), np.nan)

    # Populate the raster data with ground values
    for (x, y), value in zip(coordinates, ground_values):
        col = (x - min_x) // resolution
        row = (max_y - y) // resolution
        raster_data[row, col] = value

    # Define the transform (affine transformation matrix)
    transform = from_origin(min_x, max_y, resolution, resolution)

    # Write the raster data to a TIFF file
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=raster_data.shape[0],
        width=raster_data.shape[1],
        count=1,
        dtype=raster_data.dtype,
        crs="EPSG: 32616",
        transform=transform,
        nodata=np.nan,
    ) as dst:
        dst.write(raster_data, 1)


if __name__ == "__main__":

    # for file in pts metric that ends in txt

    df = pd.read_csv(
        "data/la_selva/pts_metric/823373.6_1155000.0.metric.txt",
        delimiter=" ",
        header=0,
    )

    # Example usage
    file_path = "data/la_selva/pts_metric/823373.6_1155000.0.metric.txt"
    output_tiff_path = "data/test/output_laselva_als.tif"

    coords, ground_values = read_text_file(file_path)
    print(ground_values)
    create_tiff(coords, ground_values, output_tiff_path)

    """   for index, row in df.iterrows():
            true_height = row.iloc[1]

            # height calculated by gedi processing
            gedi_height = row.iloc[5]
            slope = row.iloc[3]
            cover = row.iloc[4]
            print("ALS", true_height, "cover", cover, "slope", slope)"""

    topen = rasterio.open(output_tiff_path)
    tread = topen.read(1)
    # masked = np.where(tread == -1000000.0)
    masked = ma.masked_where(tread == -1000000.0, tread)
    # print(tread)tread
    one_plot(masked, output_tiff_path)

    # how to assign beam id back to las files? share coords but whereeee are they.

    # need to make 30m resolution grid from als height
    # but how to get bounds, crs,,,, coords,,,
