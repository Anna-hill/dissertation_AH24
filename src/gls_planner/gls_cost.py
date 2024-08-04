"""Using values from Lowe et al. (2024), estimate cost of global lidar system in USD """

import argparse


def readCommands():
    """
    Read commandline arguments
    """
    p = argparse.ArgumentParser(
        description=("Writes out properties of GEDI waveform files")
    )
    p.add_argument(
        "--sat_count",
        dest="satCount",
        type=int,
        default=1,
        help=("Number of satellites\nDefault 1"),
    )
    cmdargs = p.parse_args()
    return cmdargs


def sat_cost(count):
    # Total estimated cost for a year's operations in
    platform_cost = 10000 * count
    launch_cost = 1350 * count
    optics_cost = 844 * count
    data_cost = 500 * count  # approximate
    total_cost = platform_cost + launch_cost + optics_cost + data_cost
    initial_cost = ((total_cost - data_cost) / total_cost) * 100
    operational_costs = 100 - initial_cost
    print(f"System with {count} satellites: total cost ${total_cost}kUS")
    print(f"Cost of platforms: ${platform_cost}kUS")
    print(f"Cost of launch: ${launch_cost}kUS")
    print(f"Cost of optics: ${optics_cost}kUS")
    print(f"Cost of data downlink: ${data_cost}kUS")
    print(
        f"Cost to build and launch mission: {initial_cost:.2f}%, cost of operation: {operational_costs:.2f}%"
    )


if __name__ == "__main__":
    cmdargs = readCommands()
    count = cmdargs.satCount
    sat_cost(count)
