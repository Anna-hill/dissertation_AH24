"""Functions to support data visualisation"""

from matplotlib import pyplot as plt


def two_plots(data, data2, outname, title):
    """Plot 2 datasets on subplots, used to quickly check results for each tile

    Args:
        data (array): Data set
        data2 (array): Different data set
        outname (str): output file name
    """
    # set plot settings
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["figure.figsize"] = (8, 6)
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["xtick.major.size"] = 2
    plt.rcParams["xtick.major.width"] = 0.4
    plt.rcParams["xtick.major.pad"] = 2
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["ytick.major.size"] = 2
    plt.rcParams["ytick.major.width"] = 0.4
    plt.rcParams["ytick.major.pad"] = 2
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.labelpad"] = 2
    plt.rcParams["axes.titlesize"] = 16
    plt.rcParams["axes.titlelocation"] = "center"

    fig = plt.figure()
    fig.suptitle(title, fontsize="large")
    ax1 = fig.add_subplot(121)
    fig1 = ax1.imshow(data, origin="upper", cmap="Spectral")

    fig.colorbar(
        fig1,
        ax=ax1,
        label="Elevation difference (m)",
        orientation="horizontal",
        pad=0.1,
    )

    ax2 = fig.add_subplot(122)

    fig2 = ax2.imshow(
        data2,
        origin="upper",
        cmap="Greens",
        vmin=0,
        vmax=1,
    )

    fig.colorbar(
        fig2, ax=ax2, label="Canopy Cover (%)", orientation="horizontal", pad=0.1
    )
    fig.savefig(outname)
    plt.close()


def one_plot(data, outname, cmap, caption):
    """Plot a single dataset

    Args:
        data (array): Data to plot
        outname (str): Output file name
    """
    # set plot settings
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.constrained_layout.use"] = True
    plt.rcParams["xtick.labelsize"] = 8
    plt.rcParams["xtick.major.size"] = 2
    plt.rcParams["xtick.major.width"] = 0.4
    plt.rcParams["xtick.major.pad"] = 2
    plt.rcParams["ytick.labelsize"] = 8
    plt.rcParams["ytick.major.size"] = 2
    plt.rcParams["ytick.major.width"] = 0.4
    plt.rcParams["ytick.major.pad"] = 2
    plt.rcParams["axes.labelsize"] = 10
    plt.rcParams["axes.linewidth"] = 0.5
    plt.rcParams["axes.titlesize"] = 16

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fig1 = ax1.imshow(data, origin="upper", cmap=cmap)
    fig.colorbar(fig1, ax=ax1, label=caption)

    plt.savefig(f"{outname}.png")
    print(f"Figure saved to {outname}.png")
    plt.close()


def folder_colour(study_site):
    """Returns hexcode to det distinct colour fo reach site

    Args:
        study_site (str): study site name

    Returns:
        Assigned Hex code for each site
    """
    colours = {
        "Bonaly": "#003f5c",
        "hubbard_brook": "#339933",
        "la_selva": "#ffbf00",
        "nouragues": "#5900b3",
        "oak_ridge": "#d45087",
        "paracou": "#3399ff",
        "robson_creek": "#cc3300",
        "wind_river": "#ff8000",
        "test": "#665191",
        "all": "#C0D6E4",
    }
    if study_site in colours:
        return colours[study_site]

    # Unrecognised sites return as black
    return "#000000"
