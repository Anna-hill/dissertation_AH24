import os
import time
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
                f"Sim_{file}.h5",
                "-hdf",
            ]
        )
        print("The exit code was: %d" % rat_files.returncode)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    study_area = cmdargs.studyArea

    # find las file in arg-defined study area folder
    # find bounds of las file
    extractBounds(study_area)
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
