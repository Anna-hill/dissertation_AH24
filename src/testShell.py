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
        default="0",
        help=("Number of photon in simulated waveform. -1 to add a set of options"),
    )

    cmdargs = p.parse_args()
    return cmdargs


def filePath(folder):
    """Function to test file paths and glob"""

    filePath = f"data/{folder}/raw_las"

    file_list = glob(filePath + "/*.las")

    return file_list


def extractBounds(folder):
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
        outname = f"data/{folder}/sim_waves/Sim_{bounds[0]}{bounds[1]}.h5"

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
            ]
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
        ]
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
        5,
        10,
        100,
    ]  # change values to appropriate noise settings
    photon_count = [200, 150, 100, 50]

    # 4 differnt options to allow different combinations of variation for gediMetric command

    # All noises all photons options
    if noise == -1 and photons == -1:
        for idx, file in enumerate(file_list):
            for nPhotons in photon_count:
                for iNoise in noise_levels:
                    outroot = f"data/{folder}/pts_metric/{idx}_p{nPhotons}_n{iNoise}"
                    print(
                        f"working on {folder} {idx + 1} of {len(file_list)}, photons: {nPhotons} noise: {iNoise}"
                    )
                    metricCommand(file, outroot, nPhotons, iNoise)

    # All noises but only 1 photon value
    elif noise == -1 and photons != -1:
        for idx, file in enumerate(file_list):
            for iNoise in noise_levels:
                outroot = f"data/{folder}/pts_metric/{idx}_p{photons}_n{iNoise}"
                print(
                    f"working on {folder} {idx + 1} of {len(file_list)}, photons: {photons} noise: {iNoise}"
                )
                metricCommand(file, outroot, photons, iNoise)

    # Only 1 noise level but all photon options
    elif noise != -1 and photons == -1:
        for idx, file in enumerate(file_list):
            for nPhotons in photon_count:
                outroot = f"data/{folder}/pts_metric/{idx}_p{nPhotons}_n{noise}"
                print(
                    f"working on {folder} {idx + 1} of {len(file_list)}, photons: {nPhotons} noise: {noise}"
                )
                metricCommand(file, outroot, nPhotons, noise)

    # 1 noise level and 1 photon count
    else:
        for file in file_list:
            outroot = f"data/{folder}/pts_metric/{idx}_p{photons}_n{noise}"
            print(
                f"working on {folder} {idx + 1} of {len(file_list)}, photons: {photons} noise: {noise}"
            )
            metricCommand(file, outroot, photons, noise)


if __name__ == "__main__":
    t = time.perf_counter()

    cmdargs = gediCommands()
    all_sites = cmdargs.everyWhere
    set_noise = cmdargs.noise
    set_pCount = cmdargs.pCount

    # process all sites
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
            extractBounds(site)
            runMetric(site, set_noise, set_pCount)

    # Only process given site
    else:
        study_area = cmdargs.studyArea
        print(f"working on {study_area}")
        extractBounds(study_area)
        runMetric(study_area, set_noise, set_pCount)

    # in python window in terminal:
    # sanity check of hdf5 files (better way later)
    #    >>> import h5py
    #    >>> filename = "data/Bonaly/sim_waves/Sim_321000.0666000.0.h5"
    #    >>> f = h5py.File(filename, "r")
    #    >>> list(f)
    #    >>> list(f["LAT0"])

    # then we need a lastools shell

    # Test efficiency
    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
