import time
import subprocess
import argparse
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

    p.add_argument(
        "--everywhere",
        dest="everyWhere",
        type=int,
        default="0",
        help=("Whether to run code on all study sites, 0 no, 1 yes"),
    )

    cmdargs = p.parse_args()
    return cmdargs


def testFilepath(folder):
    filePath = f"data/{folder}/raw_las"

    file_list = glob(filePath + "/*.las")

    print(file_list)


def extractBounds(folder):
    filePath = f"data/{folder}/raw_las"

    file_list = glob(filePath + "/*.las")

    print(file_list)
    for idx, file in enumerate(file_list):
        bounds = lasBounds.lasMBR(file)
        print(f"working on {folder} {idx + 1} of {len(file_list)}, bounds = {bounds}")
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
        # Currently looks weird because i have text file from past gedi metric run and they don't match
        # python3	$GEDIRAT_ROOT/gediHandler.py --input data/Bonaly/sim_waves/Sim_320000.0665000.0.h5 --outRoot data/Bonaly/shell_plots/


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere

    # find las file in arg-defined study area folder
    # find bounds of las file

    if all_sites > 0:
        study_sites = [
            "Bonaly",
            "hubbard_brook",
            "la_selva",
            "nourages",
            "oak_ridge",
            "paracou",
            "robson_creek",
            "wind_river",
        ]
        print(f"working on all sites ({all_sites})")
        for site in study_sites:
            # testFilepath(site)
            extractBounds(site)
            # come back to this later
            # don't want to run code on all until thoroughly tested
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
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
    print(t)
