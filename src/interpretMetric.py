"""Functions to support DTM shell, extracts values from ALS text files"""

import numpy as np
import rasterio
from rasterio.transform import from_origin
import re


# Function to read the text file and extract data
def read_text_file(file_path):
    """Open text file and extract values"""

    coordinates = []
    ground_values = []
    canopy_values = []
    slope_values = []
    top_height = []

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

                # extract canopy top height
                top_value = float(id_line.split()[2])
                top_height.append(top_value)

                # extract canopy value
                canopy_value = float(id_line.split()[4])
                canopy_values.append(canopy_value)

                # extract slope value
                slope_value = float(id_line.split()[3])
                slope_values.append(slope_value)

    return coordinates, ground_values, canopy_values, slope_values, top_height


def create_geo_array(coordinates, ground_values, resolution=30):
    """Create array of ALS values at coordinate locations"""

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
    """Create geotiff from ALS metric information"""

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


def metric_functions(coords, data, outname, epsg):
    """Joins als metric functions"""

    # make als ground tiff
    raster_data, bounds = create_geo_array(coords, data)
    create_tiff(raster_data, bounds, epsg, outname)

    return raster_data
