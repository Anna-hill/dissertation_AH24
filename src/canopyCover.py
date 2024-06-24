"""Test script to extract canopy cover metrics, after using lastools canopyShell.bat shell script"""

import rasterio
import glob
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
from shapely.geometry import box
from rasterio.plot import show
from rasterio.warp import reproject, Resampling


def plotImage(raster):
    """Make a figure from the difference DTM

    Args:
        raster (arr): data to plot
           outname (str): output image name
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig1 = ax1.imshow(raster, origin="lower", cmap="Greens")
    fig.colorbar(fig1, ax=ax1, label="Canopy cover(%)")
    plt.show()
    # plt.clf()


def findCC(tif):
    # cc arrays different shape to als arrays. likely to cause issues so taking out summary stats

    tif_open = rasterio.open(tif)
    tif_read = tif_open.read(1)
    print(
        "canopy cover shape: ",
        tif_read.shape,
    )
    # make mask of data points
    masked_data = ma.masked_where(tif_read == -9999, tif_read)
    # data_mask = tif_read != -9999

    # filter out no data values
    # valid_arr = tif_read[data_mask]
    plotImage(masked_data)
    # flattening array makes calcuations easier
    flat_arr = masked_data.flatten()

    mean_CC = np.mean(flat_arr)
    stdDev_CC = np.std(flat_arr)

    # CC contains no data values (-9999)

    # What i would like this function to do:
    # find mean CC value
    # find stDev of canopy cover

    # make a canopy cover image
    # is it worth having 121 subplot where canopy cover is included against the difference???
    return mean_CC, stdDev_CC, masked_data


def read_raster_and_extent(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1)  # Read the first band
        # make mask of data points
        masked_data = ma.masked_where(data == -9999, data)
        affine = src.transform
        crs = src.crs
        bounds = src.bounds
        extent = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
    return masked_data, affine, crs, extent


def check_intersection(extent1, extent2, threshold=0.8):
    """Check whether two polygons have intersecting areas over a given threshold

    Args:
        extent1 (shapely polygon): bounding box of tif file
        extent2 (shapely polygon): bounding box of tif file
        threshold (float, optional): level of interesction needed. Defaults to 0.9.

    Returns:
        bool: whether or not intersection is significant
    """

    intersection = extent1.intersection(extent2)
    if intersection.is_empty:
        return False

    intersection_area = intersection.area
    extent1_area = extent1.area
    extent2_area = extent2.area

    return (intersection_area / extent1_area >= threshold) and (
        intersection_area / extent2_area >= threshold
    )


# Function to resample raster to match another raster's shape and transform
def resample_raster(
    src_data, src_transform, src_crs, dst_shape, dst_transform, dst_crs
):

    dst_data = np.empty(dst_shape, dtype=src_data.dtype)
    # masked_data = ma.masked_where(src_data == -9999, src_data)

    reproject(
        source=src_data,
        destination=dst_data,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=Resampling.average,
        src_nodata=-9999,
        dst_nodata=-999,
    )
    return dst_data


def plot_dtms(dtm1, dtm2, title1, title2):
    # Assuming dtm1 and dtm2 are numpy arrays representing the DTMs

    fig, axs = plt.subplots(1, 2, figsize=(12, 6))  # Create a figure with two subplots

    # Plot DTM 1
    im1 = axs[0].imshow(dtm1, cmap="Spectral")
    axs[0].set_title(title1)
    fig.colorbar(im1, ax=axs[0])  # Add colorbar for DTM 1

    # Plot DTM 2
    im2 = axs[1].imshow(dtm2, cmap="Greens")
    axs[1].set_title(title2)
    fig.colorbar(im2, ax=axs[1])  # Add colorbar for DTM 2

    # plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # file = "data/test/als_canopy/000073_las_dns.tif"
    # mean, stddev, raster = findCC(file)
    # print("mean CC is ", mean, "StdDev is ", stddev)

    # file2 = "data/test/als_dtm/826000.0_1149352.8.tif"
    # findCC(file2)

    # dtm_path = "data/test/als_dtm/826000.0_1149352.8.tif"
    # canopy_cover_path = "data/test/als_canopy/000073_las_dns.tif"

    # Directory paths
    dtm_dir = "data/test/diff_dtm"
    canopy_cover_dir = "data/test/als_canopy"

    # List all files
    dtm_files = sorted(glob.glob(dtm_dir + "/*.tif"))
    canopy_cover_files = sorted(glob.glob(canopy_cover_dir + "/*.tif"))

    # Read all extents for dtm and canopy cover files
    dtm_extents = {f: read_raster_and_extent(f)[3] for f in dtm_files}
    canopy_cover_extents = {f: read_raster_and_extent(f)[3] for f in canopy_cover_files}

    # Find matching files based on spatial extents
    matches = []
    for dtm_file, dtm_extent in dtm_extents.items():
        for canopy_file, canopy_extent in canopy_cover_extents.items():
            if dtm_extent.intersects(canopy_extent):
                matches.append((dtm_file, canopy_file))
                break  # Assuming one-to-one match

    for dtm_file, canopy_file in matches:
        dtm, dtm_affine, dtm_crs, _ = read_raster_and_extent(dtm_file)
        canopy_cover, canopy_cover_affine, canopy_cover_crs, _ = read_raster_and_extent(
            canopy_file
        )
        # print(canopy_cover)

        # make mask of data points
        masked_data = ma.masked_where(canopy_cover < 0, canopy_cover)
        # print(canopy_cover)

        resampled_canopy_cover = resample_raster(
            masked_data,
            canopy_cover_affine,
            canopy_cover_crs,
            dtm.shape,
            dtm_affine,
            dtm_crs,
        )
        mean1 = np.mean(canopy_cover)
        std1 = np.std(canopy_cover)
        # print(resampled_canopy_cover)

        masked_data2 = ma.masked_where(
            resampled_canopy_cover < 0, resampled_canopy_cover
        )

        mean_canopy_cover = np.nanmean(masked_data2)
        std_canopy_cover = np.nanstd(masked_data2)

        print(f"DTM File: {dtm_file}")
        print(f"Canopy Cover File: {canopy_file}")
        print(f"min val: {np.min(resampled_canopy_cover)}")
        print(f"Mean Canopy Cover: {mean_canopy_cover}")
        print(f"Standard Deviation of Canopy Cover: {std_canopy_cover}")

        plot_dtms(
            dtm,
            masked_data2,
            title1="Elevation (m)",
            title2="Canopy Cover (%)",
        )
