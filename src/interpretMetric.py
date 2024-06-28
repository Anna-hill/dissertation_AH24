import pandas as pd
import numpy as np

# group imports
import numpy.ma as ma
import rasterio
from rasterio.transform import from_origin
import re
from plotting import one_plot


# Function to read the text file and extract data
def read_text_file(file_path):
    coordinates = []
    ground_values = []
    canopy_values = []
    slope_values = []

    with open(file_path, "r") as file:
        lines = file.readlines()
        # Process lines one at a time
        for i in range(0, len(lines)):
            id_line = lines[i].strip()

            # Extract coordinates from the ID line
            match = re.search(r"gediWave\.(\d+)\.(\d+)", id_line)
            if match:
                x, y = map(int, match.groups())
                coordinates.append([x, y])

                # Extract the ground value
                ground_value = float(id_line.split()[1])
                ground_values.append(ground_value)

                # extract canopy value
                canopy_value = float(id_line.split()[4])
                canopy_values.append(canopy_value)

                # extract slope value
                slope_value = float(id_line.split()[3])
                slope_values.append(slope_value)

    return coordinates, ground_values, canopy_values, slope_values


def create_geo_array(coordinates, ground_values, resolution=30):
    # Convert coordinates and ground values to numpy arrays
    coordinates = np.array(coordinates)
    ground_values = np.array(ground_values, dtype="float32")

    ground_values[ground_values == -1000000.00] = -999

    # Determine the bounds of the raster
    min_x, min_y = coordinates.min(axis=0)
    max_x, max_y = coordinates.max(axis=0)

    # Save coords in list
    bounds = [min_x, min_y, max_x, max_y]

    # Determine the size of the raster
    width = (max_x - min_x) // resolution + 1
    height = (max_y - min_y) // resolution + 1

    # Create an empty array for the raster data
    raster_data = np.full((height, width), -999, dtype="float32")

    # Populate the raster data with ground values
    for (x, y), value in zip(coordinates, ground_values):
        col = (x - min_x) // resolution
        row = (max_y - y) // resolution
        raster_data[row, col] = value

    return raster_data, bounds


def create_tiff(raster_data, bounds, epsg, output_path, resolution=30):

    # Grid built with coords at top left of each pixel
    transform = from_origin(
        bounds[0] + (resolution / 2),
        bounds[3] - (resolution / 2),
        resolution,
        resolution,
    )

    # Write the raster data to a TIFF file
    with rasterio.open(
        f"{output_path}.tif",
        "w",
        driver="GTiff",
        height=raster_data.shape[0],
        width=raster_data.shape[1],
        count=1,
        dtype=raster_data.dtype,
        crs=f"EPSG: {epsg}",
        transform=transform,
        nodata=-999,
    ) as dst:
        dst.write(raster_data, 1)


def metric_functions(coords, data, cmap, caption, outname, epsg):
    """come back later to tidy this one up"""

    # make als ground tiff
    raster_data, bounds = create_geo_array(coords, data)
    # create_tiff(raster_data, bounds, epsg, outname)  # removed for efficiency

    # mask no data and visualise
    # open = rasterio.open(output_path)
    # read = open.read(1)

    # masked = ma.masked_where(raster_data == -999, raster_data)

    # one_plot(masked, outname, cmap, caption)  # removed for efficiency

    return raster_data


if __name__ == "__main__":

    # for file in pts metric that ends in txt
    file_path = "data/la_selva/pts_metric/823374_1155000.metric.txt"
    output_als_path = "data/test/output_laselva_als.tif"
    output_canopy_path = "data/test/output_laselva_canopy.tif"
    output_slope_path = "data/test/output_laselva_slope.tif"

    coords, ground_values, canopy_values, slope_values = read_text_file(file_path)

    # make als ground tiff
    raster_data, bounds = create_geo_raster(coords, ground_values)
    create_tiff(raster_data, bounds, output_als_path)

    # mask no data and visualise
    topen = rasterio.open(output_als_path)
    tread = topen.read(1)
    masked = ma.masked_where(tread == -1000000.0, tread)
    one_plot(masked, output_als_path, cmap="Spectral", caption="Elevation (m)")

    # make als canopy tiff
    canopy_data, bounds = create_geo_raster(coords, canopy_values)
    create_tiff(canopy_data, bounds, output_canopy_path)

    # mask no data and visualise
    topen = rasterio.open(output_canopy_path)
    tread = topen.read(1)
    masked = ma.masked_where(tread == -1000000.0, tread)
    one_plot(masked, output_canopy_path, cmap="Greens", caption="Canopy cover (%)")

    # make slope tiff
    slope_data, bounds = create_geo_raster(coords, slope_values)
    create_tiff(slope_data, bounds, output_slope_path)

    # mask no data and visualise
    topen = rasterio.open(output_slope_path)
    tread = topen.read(1)
    masked = ma.masked_where(tread == -1000000.0, tread)
    one_plot(masked, output_slope_path, cmap="Blues", caption="Slope (%) or angle")
