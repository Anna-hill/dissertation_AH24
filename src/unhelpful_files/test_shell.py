import os
import subprocess
import h5py
from glob import glob
import lasBounds


# Run GediRat to simulate waveforms


def bounds_run(map_lidarPath, file_list, epsg):
    # epsg for wind river
    try:
        for file in file_list:
            list_bounds = subprocess.run(
                [map_lidarPath, f"-input {file}", "-writeBound", f"-epsg {epsg}"]
            )
            print("The exit code was: %d" % list_bounds.returncode)
            # os.system(f"MapLidar -input {file} -writeBound -epsg {32610}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print("Error output:", e.stderr)


if __name__ == "__main__":
    os.system("pwd")
    os.system("cd ~")
    os.system("ls -la")

    # home_dir = os.system("cd src/")
    # print("`cd src` ran with exit code %d" % home_dir)

    # home_dir = subprocess.run(["cd", "src/"])
    # print("exit code was  %d" % home_dir.returncode)

    # list_files = subprocess.run(["ls", "-l"])
    # print("The exit code was: %d" % list_files.returncode)

    # Try looping later?
    study_area = "wind_river"

    # set to cmdarg as default, but option to change
    filePath = (
        f"/exports/csce/datastore/geos/groups/MSCGIS/s2559258/{study_area}/raw_las"
    )

    file_list = glob(filePath + "/*.las")

    print(file_list)

    epsg = 32610
    map_lidarPath = "/home/s2559258/src/gedisimulator/mapLidar.c"

    bounds_run(map_lidarPath, file_list, epsg)

# apply looping on bounds

print(f"working on: {bounds}")

# vary study area and spacing?
os.system(
    f"gediRat -inList {file_list} -ground -gridBound {bounds} -gridStep {30} -output {study_area}.h5 -hdf"
)

print(f"Simulated waveforms output to {study_area}.h5")


# Gedi metric run (finesse???)
os.system(
    f"gediMetric -input {study_area}.h5 -readHDFgedi -ground -varScale 3.5 -sWidth 0.8 -rhRes 2 -laiRes 5"
)


# look in file ???
filename = "{study_area}.h5"
f = h5py.File(filename, "r")
list(f)
list(f["LAT0"])

# Make plots for sanity check
os.system(
    f"python3	$GEDIRAT_ROOT/gediHandler.py --input {GediRat_output}.h5 --outRoot {study_area}plots"
)


# Make sim waves into points
# vary photon countS
os.system(
    f"gediMetric -input {GediRat_output}.h5 -readHDFgedi -outRoot {study_area}Points -photonCount -nPhotons {photonN}"
)

print(f"H5 file {GediRat_output}.h5 conveted to {study_area}Points.pts")
