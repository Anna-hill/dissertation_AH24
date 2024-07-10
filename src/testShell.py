"""Run gediSimulator to simulate full-waveforms from ALS files"""

import time
import itertools
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

    p.add_argument(
        "--noise",
        dest="noise",
        type=int,
        default="0",
        help=("Level of noise to be added to waveform. -1 to add a set of options"),
    )

    p.add_argument(
        "--pcount",
        dest="pCount",
        type=int,
        default="100",
        help=("Number of photon in simulated waveform. -1 to add a set of options"),
    )

    cmdargs = p.parse_args()
    return cmdargs


# Do i need this????
def filePath(folder):
    """Function to test file paths and glob"""

    filePath = f"data/{folder}/raw_las"

    file_list = glob(filePath + "/*.las")

    return file_list


def runGRat(folder):
    """Function to run gediRat (waveform simulation) on las files in a folder

    Args:
        folder (str): folder for specified study site
    """

    # Identify files in folders
    filePath = f"data/{folder}/raw_las"
    file_list = glob(filePath + "/*.las")

    for idx, file in enumerate(file_list):
        # Retrieve bounds of las files
        bounds = lasBounds.lasMBR(file)
        print(f"working on {folder} {idx + 1} of {len(file_list)}, bounds = {bounds}")
        outname = f"data/{folder}/sim_waves/{bounds[0]}_{bounds[1]}.h5"

        # Run gediRat in command line
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
            ],
            check=True,
        )

        print("The exit code was: %d" % rat_files.returncode)


def metricCommand(input, outRoot, nPhotons, noise):
    """Define framework for gediMetric comands

    Args:
        input (str): input hdf5 file
        outRoot (str): output file path
        nPhotons (int): number of photons per waveform
        noise (int): number of noise photons per waveform
    """
    gedi_metric = subprocess.run(
        [
            "gediMetric",
            "-input",
            f"{input}",
            "-readHDFgedi",
            "-outRoot",
            f"{outRoot}",
            "-photonCount",
            "-nPhotons",
            f"{nPhotons}",
            "-ground",
            "-noiseMult",
            f"{noise}",
        ],
        check=True,
    )
    print("The exit code was: %d" % gedi_metric.returncode)


def metricText(folder):
    """Run gediMetric to get text file of metrics (slope, canopy cover, als ground)

    Args:
        folder (str): name of site to investigate
    """

    filePath = f"data/{folder}/sim_waves"
    file_list = glob(filePath + "/*.h5")
    for file in file_list:
        clipFile = lasBounds.clipNames(file, ".h5")
        outname = f"data/{folder}/pts_metric/{clipFile}"
        # Define and run command
        gedi_metric = subprocess.run(
            [
                "gediMetric",
                "-input",
                f"{file}",
                "-readHDFgedi",
                "-outRoot",
                f"{outname}",
                "-ground",
                "-noRHgauss",
            ],
            check=True,
        )
        print("The exit code was: %d" % gedi_metric.returncode)


def runMetric(folder, noise, photons):
    """Use gediMetric to convert hdf5 outputs of gedirat simulation into .pts files
        Also vary noise and photon count

    Args:
        folder (str): name of study site
        noise (int): noise level. -1 will trigger multiple options
        photons (int): photon count per waveform. -1 will trigger multiple options
    """

    # Find file names
    filePath = f"data/{folder}/sim_waves"
    file_list = glob(filePath + "/*.h5")

    noise_levels = [
        0,
        4,
        # 5.3,
        8,
        15,
        104,
        149,
        # 200,
        # 300,
        # 400,
        # 500,
    ]
    photon_count = [149, 300, 500]

    # 4 different options to allow different combinations of variation for gediMetric command
    # All noises all photons options
    if noise == -1 and photons == -1:
        # itertools to avoid too many nested loops
        for file, nPhotons, iNoise in itertools.product(
            file_list, photon_count, noise_levels
        ):
            clipFile = lasBounds.clipNames(file, ".h5")
            print(f"working on {clipFile}, photons: {nPhotons} noise: {iNoise}")
            outroot = f"data/{folder}/pts_metric/{clipFile}_p{nPhotons}_n{iNoise}"
            metricCommand(file, outroot, nPhotons, iNoise)

    # All noises but only 1 photon value
    elif noise == -1 and photons != -1:
        for file, iNoise in itertools.product(file_list, noise_levels):
            clipFile = lasBounds.clipNames(file, ".h5")
            outroot = f"data/{folder}/pts_metric/{clipFile}_p{photons}_n{iNoise}"
            print(f"working on {clipFile}, photons: {photons} noise: {iNoise}")
            metricCommand(file, outroot, photons, iNoise)

    # Only 1 noise level but all photon options
    elif noise != -1 and photons == -1:
        for file, nPhotons in itertools.product(file_list, photon_count):
            clipFile = lasBounds.clipNames(file, ".h5")
            outroot = f"data/{folder}/pts_metric/{clipFile}_p{nPhotons}_n{noise}"
            print(f"working on {clipFile}, photons: {nPhotons} noise: {noise}")
            metricCommand(file, outroot, nPhotons, noise)

    # 1 noise level and 1 photon count
    else:
        for file in file_list:
            clipFile = lasBounds.clipNames(file, ".h5")
            outroot = f"data/{folder}/pts_metric/{clipFile}_p{photons}_n{noise}"
            print(
                f"working on {folder} of {len(file_list)}, photons: {photons} noise: {noise}"
            )
            metricCommand(file, outroot, photons, noise)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    study_area = cmdargs.studyArea
    set_noise = cmdargs.noise
    set_pCount = cmdargs.pCount

    # process all sites
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
        print(f"working on all sites {study_sites}")
        for site in study_sites:
            runGRat(site)
            metricText(site)
            runMetric(site, set_noise, set_pCount)

    # Only process given site
    else:
        print(f"working on {study_area}")
        runGRat(study_area)
        metricText(study_area)
        runMetric(study_area, set_noise, set_pCount)

    # Test efficiency
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
