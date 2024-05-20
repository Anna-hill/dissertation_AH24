import os
import time
import h5py
import subprocess
import argparse
import h5py
from glob import glob
import lasBounds


def gediCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(description=("Test data fusion model for Bonaly"))

    p.add_argument(
        "--studyarea",
        dest="studyArea",
        type=str,
        default="Bonaly",
        help=("Study area name"),
    )

    cmdargs = p.parse_args()
    return cmdargs


def extractBounds(folder):
    filePath = f"data/{folder}/raw_las"

    file_list = glob(filePath + "/*.las")

    print(file_list)
    for idx, file in enumerate(file_list):
        bounds = lasBounds.lasMBR(file)
        print(f"working on file {idx + 1} of {len(file_list)}, bounds = {bounds}")
        outname = f"data/{folder}/sim_waves/Sim_{bounds[0]}{bounds[1]}.h5"

        rat_files = subprocess.run(
            [
                "gediRat",
                "-input",
                file,
                "-ground",
                "-gridBound",
                str(bounds[0]),
                str(bounds[2]),
                str(bounds[1]),
                str(bounds[3]),
                "-gridStep",
                "30",
                "-output",
                outname,
                "-hdf",
            ]
        )

        print("The exit code was: %d" % rat_files.returncode)

        """plot_rats = subprocess.run(
            [
                "python3",
                "$GEDIRAT_ROOT/gediHandler.py",
                "--input",
                outname,
                "--outRoot",
                f"data/{folder}/sim_waves/new_plots",
            ]
        )

        print("The exit code was: %d" % plot_rats.returncode)"""
        # The following command works in linux, but likely to be slower than alternatives
        # Currently looks wierd because i have text file from past gedi metric run and they don't match
        # python3	$GEDIRAT_ROOT/gediHandler.py --input data/Bonaly/sim_waves/Sim_320000.0665000.0.h5 --outRoot data/Bonaly/shell_plots/


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    study_area = cmdargs.studyArea

    # find las file in arg-defined study area folder
    # find bounds of las file
    extractBounds(study_area)

    # in python window in terminal:
    # sanity check of hdf5 files (better way later)
    #    >>> import h5py
    #    >>> filename = "data/Bonaly/sim_waves/Sim_321000.0666000.0.h5"
    #    >>> f = h5py.File(filename, "r")
    #    >>> list(f)
    #    >>> list(f["LAT0"])

    # looping on bounds (OOSA), i.e. find bounds of 1/4 of las file
    # Run GediRat to simulate waveforms in each quarter
    # example:
    # gediRat -inList /exports/csce/datastore/geos/groups/MSCGIS/s2559258/Bonaly/raw_las/raw_las.txt -ground -gridBound 320752.6395 321370.4455 665697.0768 666632.639 -gridStep 20 -output grid.h5 -hdf

    ## print(f"working on: {bounds}")

    # move on to other quarters, then other files

    # Once simulated, will need to run GEDImetric, then convert to pts
    # then we need a lastools shell
    # Test efficiency
    t = time.perf_counter() - t
