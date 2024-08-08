"""Script to run dtmShell with differnt las options"""

import subprocess
import time
from dtmShell import gediCommands


def run_dtmShell(folder, las_settings, interpolation, int_meth):
    """Runs command for dtmShell

    Args:
        folder (str): study site
        las_settings (str): lastools settings code
        interpolation (bool): Whether to perform interpolation
        int_meth (str): Interpolation function
    """
    run_dtm = subprocess.run(
        [
            "python3",
            "src/dtmShell.py",
            "--studyarea",
            f"{folder}",
            "--lassettings",
            f"{las_settings}",
            "--interpolate",
            f"{interpolation}",
            "--int_method",
            f"{int_meth}",
        ],
        check=True,
    )

    print("The exit code was: %d" % run_dtm.returncode)


if __name__ == "__main__":
    t = time.perf_counter()
    cmdargs = gediCommands()
    study_area = cmdargs.studyArea
    las_setting = cmdargs.lasSettings
    interpolation = cmdargs.interpolate
    int_meth = cmdargs.intpMethod

    if las_setting == "all":
        # Run dtmShell with all lassettings
        las_settings = [
            "40051",
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
            run_dtmShell(study_area, setting, interpolation, int_meth)
    else:
        run_dtmShell(study_area, las_setting, interpolation, int_meth)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
