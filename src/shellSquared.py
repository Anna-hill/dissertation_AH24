"""Script to run dtmShell with differnt las options. Use with caution - takes about 6 hours to run"""

import subprocess
import time
import argparse


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
        "--lassettings",
        dest="lasSettings",
        type=str,
        default="400505",
        help=("Choose input based on lastools settings applied to find gound"),
    )
    cmdargs = p.parse_args()
    return cmdargs


def run_dtmShell(folder, las_settings):
    run_dtm = subprocess.run(
        [
            "python3",
            "src/dtmShell.py",
            "--studyarea",
            f"{folder}",
            "--lassettings",
            f"{las_settings}",
            "--interpolate",
            "True",
        ],
        check=True,
    )

    print("The exit code was: %d" % run_dtm.returncode)


if __name__ == "__main__":
    t = time.perf_counter()
    cmdargs = gediCommands()
    study_area = cmdargs.studyArea
    las_setting = cmdargs.lasSettings

    if las_setting == "all":
        las_settings = [
            #"40051",
            "50051",
            "60051",
            "400501",
            "500501",
            "600501",
            "400505",
            "500505",
            "600505",
        ]
        for setting in las_settings:
            run_dtmShell(study_area, setting)
    else:
        run_dtmShell(study_area, las_setting)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
