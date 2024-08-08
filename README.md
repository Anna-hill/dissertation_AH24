# Dissertation Repository

*Anna Hill*

Scripts accompanying: 

**Developing the Next Generation of Satellite Lidars: Assessing The Utility of Airborne Lidar Processing Methods for Ground-Finding**

A complete description of the command line arguments and processing rationale is available in the accompanying technical report

<p align="center">
<img src= "gifs/rotating_nouragues.gif" alt="Rotating image example" width="600px">
</p>

# src

## testShell.py

- Uses the GEDI simulator (Hancock et al., 2019) to generate simulated photon-counting Lidar from discrete-return Airborne Lidar
- Records information from the Airborne data for later comparision

can be run with:

> python3 src/testShell.py --studyarea all --noise -1 --pcount -1

## dtmShell.py

- Uses mapLidar from the GEDI simulator to generate DTMs from ground-classified simulated waveforms
- Compares accuracy of ground finding against Airborne information

can be run with:

> python3 src/dtmShell.py --studyarea all --lassettings 40051 --interpolate True --int_method linear

## shellSquared.py

- Runs dtmShell.py multiple times with different *--lassettings* options

> python3 src/shellSquared.py --studyarea all --lassettings all --interpolate True --int_method linear

## analyseResults.py

- Converts accuracy assessment of simulated DTMs into beam sensitivty metrics
- Generates plots for comparison of results

can be run with:

> python3 src/analyseResults.py --studyarea hubbard_brook --lassettings 40051 --interpolation _linear --bs_thresh 4

## slope_cc_plot.py

- Reads merged geotiff files of results and compares the relationships between them
- makes scatter plot matrices of slope, canopy cover, linear interpolated elevation accuracy or cubic interpolated elevation accuracy

can be run with:

> python3 src/slope_cc_plot.py --studyarea all –plottype 1

## Additional scripts:

- **interpretMetric.py**,**plotting.py** and **lasBounds.py** are supporting scripts which cannot be run directly
- **gls_cost.py** performs a simple calculation of how much a global satellite lidar system would cost, based on the number of satellites:

> python3 gls_cost.py --sat_count 6

# bat

- contains the lastools batch processing scripts
- the commands within these are described in more detail in the Technical report