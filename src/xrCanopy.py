import xarray as xr
import numpy as np
import rioxarray


# Function to read a TIFF file into an xarray DataArray
def read_tiff(file_path):
    # Open the TIFF file as an xarray DataArray
    ds = xr.open_rasterio(file_path)
    # Ensure that the CRS is properly set
    ds.rio.write_crs("EPSG:32622", inplace=True)
    return ds


# Read two TIFF files into xarray DataArrays
file_path1 = "data/paracou/als_dtm/284589.5_584489.0.tif"
file_path2 = "data/paracou/sim_dtm/284589.5_584489.0_p149_n0.tif"

ds1 = read_tiff(file_path1)
ds2 = read_tiff(file_path2)

# Ensure the datasets have the same dimensions and coordinates
# Reindex ds2 to match ds1 if necessary
ds2 = ds2.reindex_like(ds1, method="nearest")

# Calculate the difference between the two datasets
ds_diff = ds1 - ds2

# Ensure the difference dataset inherits the georeferencing attributes from ds1
ds_diff.rio.write_crs(ds1.rio.crs, inplace=True)
ds_diff.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
ds_diff.attrs["transform"] = ds1.attrs["transform"]
ds_diff.attrs["crs"] = ds1.attrs["crs"]

# Add the difference as another dimension to the original dataset
# Create a new DataArray with an extra dimension for 'difference'
combined_ds = xr.Dataset({"original_1": ds1, "original_2": ds2, "difference": ds_diff})

# Save the combined dataset to a netCDF file
output_path = "data/paracou/test_netcdf.nc"
combined_ds.to_netcdf(output_path)

print(f"Combined dataset with difference saved to {output_path}")
