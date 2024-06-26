import xarray as xr
import numpy as np
import rioxarray as rxr
from sklearn.metrics import mean_squared_error, r2_score


# Function to read a tif file into an xarray DataArray
def read_tiff(file_path, epsg):
    # Open tif file as an xarray DataArray
    ds = xr.open_rasterio(file_path)
    ds.rio.write_crs(f"EPSG:{epsg}")
    return ds


def diff_dtm(dataset1, dataset2, no_data_value):
    """Create tif of difference between 2 DTMs
    # fix datatype in comments!

    Args:
        dataset1 (array): 1st array
        dataset2 (array): 2nd array
        no_data_value (int): value of no data pixels

    Returns:
        result: xarray dataset
    """
    # print(dataset1)
    # Hide no data values
    mask = (dataset1.band != no_data_value) & (dataset2.band != no_data_value)
    masked1 = dataset1.where(mask, drop=True)
    masked2 = dataset2.where(mask, drop=True)

    # extract values for metrics
    data1 = masked1[0].values
    data2 = masked2[0].values

    print("values", (data1))

    # The masking adds nan which also need dealing with
    valid_mask = ~np.isnan(data1) & ~np.isnan(data2)
    data1 = data1[valid_mask]
    data2 = data2[valid_mask]

    # print("values", (data2))

    # count no data pixels
    # size is how many points left that aren't d2
    len_mask = np.size(mask) - np.size(data2)

    # count all pixels
    # mask is true/false so all pixels in there?
    ds_len = np.size(mask)
    # find rmse
    rmse = np.sqrt(mean_squared_error(data1, data2))
    # find r2 (even though poor quality metric)
    r2 = r2_score(data1, data2)

    # calculate bias
    bias = np.mean(data1 - data2)

    # Find difference
    result = masked1 - masked2

    return result, rmse, r2, bias, len_mask, ds_len


def compare_and_xarray(ds1, ds2):

    # Ensure the datasets have the same dimensions and coordinates
    # Reindex ds2 to match ds1 if necessary
    ds2 = ds2.reindex_like(ds1, method="nearest")

    # print(ds2.values)
    # Calculate the difference between the two datasets
    ds_diff, rmse, r2, bias, len_mask, ds_len = diff_dtm(ds1, ds2, 0)
    print("metrics: ", rmse, r2, bias, len_mask, ds_len)
    # Ensure the difference dataset inherits the georeferencing attributes from ds1
    ds_diff.rio.write_crs(ds1.rio.crs, inplace=True)
    ds_diff.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    # ds_diff.attrs["transform"] = ds1.attrs["transform"]
    # ds_diff.attrs["crs"] = ds1.attrs["crs"]

    return ds_diff, rmse, r2, bias, len_mask, ds_len


def compare_and_xarray2(file_path1, file_path2):
    ds1 = read_tiff(file_path1)
    ds2 = read_tiff(file_path2)

    # Ensure the datasets have the same dimensions and coordinates
    # Reindex ds2 to match ds1 if necessary
    ds2 = ds2.reindex_like(ds1, method="nearest")

    # print(ds2.values)
    # Calculate the difference between the two datasets
    ds_diff, rmse, r2, bias, len_mask, ds_len = diff_dtm(ds1, ds2, 0)
    print(ds1)
    print("metrics: ", rmse, r2, bias, len_mask, ds_len)
    # Ensure the difference dataset inherits the georeferencing attributes from ds1
    ds_diff.rio.write_crs(ds1.rio.crs, inplace=True)
    ds_diff.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
    # ds_diff.attrs["transform"] = ds1.attrs["transform"]
    ds_diff.attrs["crs"] = ds1.attrs["crs"]

    # worth appending to netcdf dataset elsewhere?
    # Add the difference as another dimension to the original dataset
    # Create a new DataArray with an extra dimension for 'difference'
    combined_ds = xr.Dataset(
        {"original_1": ds1, "original_2": ds2, "difference": ds_diff}
    )

    # Save the combined dataset to a netCDF file
    output_path = "data/paracou/test_netcdf.nc"
    combined_ds.to_netcdf(output_path)

    print(f"Combined dataset with difference saved to {output_path}")


if __name__ == "__main__":
    # Read two TIFF files into xarray DataArrays
    file_path1 = "data/test/als_dtm/826000.0_1149352.8.tif"
    file_path2 = "data/test/sim_dtm/826000.0_1149352.8_p149_n4.tif"
    ds1 = read_tiff(file_path1)
    ds2 = read_tiff(file_path2)
    compare_and_xarray2(file_path1, file_path2)
