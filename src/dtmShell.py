""" Shell script to create DTMs and assess accuracy of simulated data"""

import time
import subprocess
import argparse
from glob import glob
import rasterio
import regex
import numpy as np
import pandas as pd
import numpy.ma as ma
from sklearn.metrics import mean_squared_error, r2_score
from scipy.interpolate import griddata
import lasBounds
from plotting import two_plots
from interpretMetric import read_text_file, metric_functions


def gediCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(
        description=("Script to create DTMs and assess accuracy of simulated data")
    )

    p.add_argument(
        "--studyarea",
        dest="studyArea",
        type=str,
        default="Bonaly",
        help=("Study area name, for all sites input 'all'"),
    )

    p.add_argument(
        "--interpolate",
        dest="interpolate",
        type=bool,
        default=False,
        help=("Whether to interpolate values of nodata points"),
    )
    p.add_argument(
        "--int_method",
        dest="intpMethod",
        type=str,
        default="linear",
        help=("No-data interpolation method; can be 'linear', 'nearest' or 'cubic'"),
    )
    p.add_argument(
        "--lassettings",
        dest="lasSettings",
        type=str,
        default="400505",
        help=("Choose input based on lastools settings applied to find gound"),
    )

    cmdargs = p.parse_args()
    return cmdargs


class DtmCreation(object):
    """
    LVIS data handler
    """

    def __init__(self):
        """Empty for now"""
        pass

    def createDTM(self, folder, las_settings):
        """Run maplidar command to create DTMs from simulated waveforms

        Args:
            folder (str): study site name for folder path
            las_settings (str): lasground settings for folder path
        """
        # Set location of sim files
        simPath = f"data/{folder}/sim_ground{las_settings}"
        sim_list = glob(simPath + "/*.las")

        # Create simulated data DTM
        for idx, sim_file in enumerate(sim_list):
            # Keep original file name
            clip_file = lasBounds.clipNames(sim_file, ".las")
            print(clip_file)
            print(f"working on {folder} {idx + 1} of {len(sim_list)}")

            # find epsg code for study area
            epsg = lasBounds.findEPSG(folder)
            outname = f"data/{folder}/sim_dtm/{las_settings}/{clip_file}_{las_settings}"

            # run mapLidar command
            create_dtm = subprocess.run(
                [
                    "mapLidar",
                    "-input",
                    f"{sim_file}",
                    "-res",
                    f"{30}",
                    "-epsg",
                    f"{epsg}",
                    "-DTM",
                    "-float",
                    "-output",
                    f"{outname}",
                ],
                check=True,
            )

            print("The exit code was: %d" % create_dtm.returncode)

    def read_metric_text(self, metric_file, folder):
        """Interpret txt file produced by gediMetric, summarising key values from ALS data (ground, canopy and slope)

        Args:
            metric_file (str): path to txt file
            folder (str): study area

        Returns:
            array: geolocated array of ALS values
        """
        clip_metric = lasBounds.clipNames(metric_file, ".txt")
        outname = f"data/{folder}/als_metric/{clip_metric}"
        epsg = lasBounds.findEPSG(folder)
        # Interpret text file
        coordinates, ground_values, canopy_values, slope_values, top_height = (
            read_text_file(metric_file)
        )
        # Convert text file values into arrays, make plots, and tifs
        als_ground = metric_functions(
            coordinates,
            ground_values,
            cmap="Spectral",
            caption="Elevation (m)",
            outname=f"{outname}_ground",
            epsg=epsg,
        )
        als_canopy = metric_functions(
            coordinates,
            canopy_values,
            cmap="Greens",
            caption="Canopy cover (%)",
            outname=f"{outname}_canopy",
            epsg=epsg,
        )
        als_slope = metric_functions(
            coordinates,
            slope_values,
            cmap="Blues",
            # check this
            caption="Slope (%) or angle",
            outname=f"{outname}_slope",
            epsg=epsg,
        )
        als_t_height = metric_functions(
            coordinates,
            top_height,
            cmap="Greens",
            caption="Top height (m)",
            outname=f"{outname}_t_height",
            epsg=epsg,
        )

        # ALS ground array then directly - from sim
        return als_ground, als_canopy, als_slope, als_t_height

    @staticmethod
    def rasterio_write(data, outname, template_raster, nodata):
        """Create output geotiff from array and pre-existing geotiff with rasterio

        Args:
            data (ndarray): data to convert into geotiff
            outname (str): output file name
            template_raster (geotiff): existing geotiff to replicate metadata
            nodata (int): no data value
        """

        with rasterio.open(
            outname,
            "w",
            driver="GTiff",
            height=template_raster.height,
            width=template_raster.width,
            count=1,
            dtype=data.dtype,
            crs=template_raster.crs,
            transform=template_raster.transform,
        ) as raster:
            raster.write(data, 1)
            raster.nodata = nodata
        print(f"Tiff written to {outname}")

    @staticmethod
    def calc_metrics(als_array, sim_array):
        """Assess differences betwen 2 DEMs

        Args:
            als_array (array): 1st array
            sim_array (array): 2nd array

        Returns:
            rmse, r2, bias, no data count: metrics
        """
        # create valid data mask; so comparison excludes nodata points

        # Is there a better way to mask?
        valid_mask = (als_array != -999) & (sim_array != 0)

        # filter out no data values
        valid_als = als_array[valid_mask]
        valid_sim = sim_array[valid_mask]

        # Flatten arrays to do stats
        flat_als = valid_als.flatten()
        flat_sim = valid_sim.flatten()

        # count data pixels
        data_count = len(flat_als)

        if len(flat_als) == 0 or len(flat_sim) == 0:
            raise ValueError("No data points found")

        # find rmse, r2 and bias
        rmse = np.sqrt(mean_squared_error(flat_als, flat_sim))
        r2 = r2_score(flat_als, flat_sim)
        bias = np.mean(flat_als - flat_sim)

        # set up empty array to fill with results
        result = np.full(als_array.shape, 0, dtype=als_array.dtype)

        # Find difference
        result[valid_mask] = als_array[valid_mask] - sim_array[valid_mask]

        return rmse, r2, bias, data_count, result

    @staticmethod
    def canopy_cover_stats(raster_data):
        """Calculate mean and standard deviation from arrays (slope and canopy cover)

        Args:
            raster_data (array): values to be summarised

        Returns:
            float: mean and std dev of input raster
        """

        # summmarise array values
        raster_data = ma.masked_where(raster_data < 0, raster_data)
        mean_cc = np.mean(raster_data)
        std_cc = np.std(raster_data)
        return mean_cc, std_cc

    def find_nodata(self, ground_elev, canopy_elev):
        """Justify heavily! function finds suitable no data value for empty pixels where ground not found.
        In real data, likely that ground mis-identified as point within canopy, therefore value is average middle of canopy as absolute height


        Args:
            ground_elev (_type_): _description_
            canopy_elev (_type_): _description_

        Returns:
            _type_: _description_
        """
        valid_mask = (ground_elev > 0) & (canopy_elev > 0)

        # justify!!!!!!!!!!!!!!!!!!!
        # find middle point of canopy
        canopy_height = (canopy_elev[valid_mask] - ground_elev[valid_mask])
        ground_mean = np.mean(ground_elev[valid_mask])
        # mean vs median?????
        # returns absolute height?
        no_data_val = np.median(canopy_height) + ground_mean
        return no_data_val

    def fill_nodata(self, array, interpolation, int_meth, no_data):
        """Apply interpolation function to fill no-data gaps in sim_dtm

        Args:
            array (array): Array containing no-data points (0 value)
            interpolation (bool): Whether to perform interpolation
            int_meth (str): Interpolation function applied to data

        Returns:
            _type_: _description_
        """
        # count no data pixels
        no_data_count = np.sum(array == 0)

        if interpolation == True:
            # Identify 0 values to be replaced
            mask = array != 0

            # grid of indices to perform interpolation at
            x, y = np.indices(array.shape)

            # Apply interpolation functions to 0 values
            array_interpolated = griddata(
                (x[mask], y[mask]),
                array[mask],
                (x, y),
                method=f"{int_meth}",
                fill_value=0,  # Values not interpolated/original data set at 0
            )

            return array_interpolated, no_data_count
        # If interpolation = False, original array returned
        else:

            # replace 0 values with appropriate no data for each tile
            array = np.where(array == 0, no_data, array)
            return array, no_data_count

    #################################################################################################

    def compareDTM(self, folder, interpolation, int_meth, las_settings):
        """Assess accuracy of simulated DTMs

        Args:
            folder (str): Study site name
            interpolation (bool): Whether to interpolate and fill no data points
            int_meth (str): If interpolating, which method to use
            las_settings (str): lasground.new setings of input sim_ground files
        """
        # Define file paths
        als_metric_path = f"data/{folder}/pts_metric"
        als_metric_list = glob(als_metric_path + "/*.txt")

        sim_path = f"data/{folder}/sim_dtm/{las_settings}"
        sim_list = glob(sim_path + "/*.tif")

        # Pair up ALS and sim files for comparison
        matched_files = lasBounds.match_files(als_metric_list, sim_list)

        # Define regex patterns to extract info from file names
        rNPhotons = r"[p]+\d+"
        rNoise = r"[n]+\d+"

        # Open lists to be appended to results
        results = {
            "Folder": [],
            "File": [],
            "nPhotons": [],
            "Noise": [],
            "RMSE": [],
            "R2": [],
            "Bias": [],
            "Mean_Canopy_cover": [],
            "Std_dev_Canopy_cover": [],
            "Mean_slope": [],
            "Std_dev_slope": [],
            "NoData_count": [],
            "Data_count": [],
        }

        # Multiple sim files for each als
        for als_metric, matched_sim in matched_files.items():
            for sim_tif in matched_sim:
                sim_open = rasterio.open(sim_tif)

                # Save file name for results
                clip_match = lasBounds.clipNames(sim_tif, ".tif")
                file_name_saved = clip_match

                # extract noise and photon count vals
                nPhotons = regex.findall(pattern=rNPhotons, string=sim_tif)[0]
                noise = regex.findall(pattern=rNoise, string=sim_tif)[0]
                nPhotons = lasBounds.removeStrings(nPhotons)
                noise = lasBounds.removeStrings(noise)

                # convert matching files to arrays
                simArray = sim_open.read(1)

                # Extract values from als files
                als_read, als_canopy, als_slope, als_height = self.read_metric_text(
                    als_metric, folder
                )
                # find nodata value
                canopy_middle = self.find_nodata(als_read, als_height)
                try:
                    """# contains over 100 waves
                    if np.count_nonzero(simArray) > 100:
                        # print(clip_match)
                        # Fill nodata gaps
                        sim_read, noData = self.fill_nodata(
                            simArray, interpolation, int_meth, canopy_middle
                        )
                    else:
                        
                        continue"""

                    if (
                        # Check array has correct shape
                        als_read.shape == simArray.shape
                        # Check array contains any ground values
                        and np.max(simArray) > 0
                        # Check array contains over 100 waves
                        and np.count_nonzero(simArray) > 100):
                        sim_read, noData = self.fill_nodata(
                            simArray, interpolation, int_meth, canopy_middle
                        )
                        rmse, rSquared, bias, lenData, difference = self.calc_metrics(
                            als_read, sim_read
                        )
                        # Save and plot tiff of difference with 0 values hidden
                        masked_diference = ma.masked_where(difference == 0, difference)

                        diff_outname = (
                            f"data/{folder}/diff_dtm/{las_settings}/{clip_match}.tif"
                        )
                        self.rasterio_write(
                            data=difference,
                            outname=diff_outname,
                            template_raster=sim_open,
                            nodata=0,
                        )

                        image_name = f"figures/difference/{folder}/CC{clip_match}.png"
                        image_title = f"Absolute error for {nPhotons} photons and {noise} noise ({folder})"
                        two_plots(masked_diference, als_canopy, image_name, image_title)
                        # extract metrics from als arrays
                        mean_cc, stdDev_cc = self.canopy_cover_stats(als_canopy)
                        mean_slope, stdDev_slope = self.canopy_cover_stats(als_slope)
                    else:
                        print(f"{clip_match} contains under 100 waves or has mismatched array shapes")
                        (
                            rmse,
                            rSquared,
                            bias,
                            noData,
                            lenData,
                            mean_cc,
                            stdDev_cc,
                            mean_slope,
                            stdDev_slope,
                        ) = (
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                            -999,
                        )

                    # save results to dictionary
                    lasBounds.append_results(
                        results,
                        Folder=folder,
                        File=file_name_saved,
                        nPhotons=nPhotons,
                        Noise=noise,
                        RMSE=rmse,
                        R2=rSquared,
                        Bias=bias,
                        Mean_Canopy_cover=mean_cc,
                        Std_dev_Canopy_cover=stdDev_cc,
                        Mean_slope=mean_slope,
                        Std_dev_slope=stdDev_slope,
                        NoData_count=noData,
                        Data_count=lenData,
                    )
                    # print(f"rmse is: {rmse}, R² is: {rSquared}, bias: {bias}")

                except ValueError as e:
                    print(f"{sim_tif} ignored due to error: {e}")
                    continue

        print(
            len(results["Folder"]),
            len(results["File"]),
            len(results["nPhotons"]),
            len(results["Noise"]),
            len(results["RMSE"]),
            len(results["R2"]),
            len(results["Bias"]),
            len(results["Mean_Canopy_cover"]),
            len(results["Std_dev_Canopy_cover"]),
            len(results["NoData_count"]),
            len(results["Data_count"]),
        )

        resultsDf = pd.DataFrame(results)
        if interpolation == True:
            outCsv = f"data/{folder}/summary_{folder}_{las_settings}_{int_meth}.csv"
        else:
            outCsv = f"data/{folder}/summary_{folder}_{las_settings}.csv"
        resultsDf.to_csv(outCsv, index=False)
        print("Results written to: ", outCsv)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    study_area = cmdargs.studyArea
    interpolation = cmdargs.interpolate
    int_meth = cmdargs.intpMethod
    las_settings = cmdargs.lasSettings

    dtm_creator = DtmCreation()

    # Option to run on all sites
    if study_area == "all":
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nouragues",
            "oak_ridge",
            "paracou",
            "robson_creek",
            "wind_river",
        ]
        print(f"working on all sites ({study_sites})")
        for site in study_sites:
            #dtm_creator.createDTM(site, las_settings)
            dtm_creator.compareDTM(site, interpolation, int_meth, las_settings)

    # Run on specified site
    else:

        print(f"working on {study_area}")
        #dtm_creator.createDTM(study_area, las_settings)
        dtm_creator.compareDTM(study_area, interpolation, int_meth, las_settings)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
