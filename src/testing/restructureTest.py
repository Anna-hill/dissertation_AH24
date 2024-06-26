import time
import itertools
import rasterio
from glob import glob
from lasBounds import clipNames, interpretName
from matplotlib import pyplot as plt


def simStuff(clip_name, noise, photons, folder):
    if noise == "n5":
        file = f"data/{folder}/sim_dtm/{clip_name}_{photons}_{noise}.3.tif"
    else:
        file = f"data/{folder}/sim_dtm/{clip_name}_{photons}_{noise}.tif"

    r_open = rasterio.open(file)
    r_array = r_open.read(1)
    outname = f"figures/efficiency/{folder}/Eff_{clip_name}_{photons}_{noise}.png"
    plt.imshow(r_array)
    plt.savefig(outname)
    print(f"saved figure to {outname}")
    plt.close()


def compareDTM(folder):
    """Assess accuracy of simulated DTMs

    Args:
        folder (_type_): _description_
    """

    als_path = f"data/{folder}/als_dtm"
    sim_path = f"data/{folder}/sim_dtm"

    # canopy_path = f"data/{folder}/als_canopy"

    als_list = glob(als_path + "/*.tif")
    sim_list = glob(sim_path + "/*.tif")
    # canopy_list = glob(canopy_path + "/*.tif")
    n_set, p_set = interpretName(sim_list)
    print(n_set, p_set)
    """for file, n, p in itertools.product(als_list, n_set, p_set):
        # print(file)
        clipped = clipNames(file, ".tif")

        simStuff(clipped, n, p, folder)"""

    for file in als_list:
        for n in n_set:
            for p in p_set:
                # print(file)
                clipped = clipNames(file, ".tif")
                simStuff(clipped, n, p, folder)
    # for file in sim_list:
    # print(file)


if __name__ == "__main__":
    t = time.perf_counter()

    study_sites = [
        # "Bonaly",
        "paracou",
        "oak_ridge",
        # "nouragues",
        # "la_selva",
        # "hubbard_brook",
        # "robson_creek",
        # "wind_river",
    ]
    for site in study_sites:
        # dtm_creator.createDTM(site)
        compareDTM(site)

    t = time.perf_counter() - t
    print("time taken: ", t, " seconds")
