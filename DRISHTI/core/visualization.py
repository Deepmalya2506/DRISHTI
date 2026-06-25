import matplotlib.pyplot as plt

from DRISHTI.utils.plot import (
    log_scale,
    percentile_stretch,
    normalize,
)


def inspect_raw_dataset(dataset):

    bands = dataset["bands"]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14,12)
    )

    fig.suptitle(
        "DFSAR Raw DN Images",
        fontsize=18,
        fontweight="bold"
    )

    for ax, (name, image) in zip(
        axes.ravel(),
        bands.items()
    ):

        stretched = percentile_stretch(image)

        im = ax.imshow(
            stretched,
            cmap="gray"
        )

        ax.set_title(name)

        ax.axis("off")

        plt.colorbar(
            im,
            ax=ax,
            shrink=0.75
        )

    plt.tight_layout()

    plt.show()



def inspect_log_dataset(dataset):

    bands = dataset["bands"]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14,12)
    )

    fig.suptitle(
        "Log-scaled DN Images",
        fontsize=18,
        fontweight="bold"
    )

    for ax, (name, image) in zip(
        axes.ravel(),
        bands.items()
    ):

        log_img = log_scale(image)

        im = ax.imshow(
            log_img,
            cmap="gray"
        )

        ax.set_title(name)

        ax.axis("off")

        plt.colorbar(
            im,
            ax=ax,
            shrink=0.75
        )

    plt.tight_layout()

    plt.show()



def inspect_histograms(dataset):

    bands = dataset["bands"]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14,10)
    )

    fig.suptitle(
        "DN Histograms",
        fontsize=18,
        fontweight="bold"
    )

    for ax, (name, image) in zip(
        axes.ravel(),
        bands.items()
    ):

        ax.hist(
            image.ravel(),
            bins=250
        )

        ax.set_title(name)

        ax.set_xlabel("DN")

        ax.set_ylabel("Frequency")

    plt.tight_layout()

    plt.show()



def inspect_log_histograms(dataset):

    bands = dataset["bands"]

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(14,10)
    )

    fig.suptitle(
        "DN Histograms (Log Scale)",
        fontsize=18,
        fontweight="bold"
    )

    for ax, (name, image) in zip(
        axes.ravel(),
        bands.items()
    ):

        ax.hist(
            image.ravel(),
            bins=250
        )

        ax.set_yscale("log")

        ax.set_title(name)

        ax.set_xlabel("DN")

        ax.set_ylabel("Frequency")

    plt.tight_layout()

    plt.show()



def inspect_mask(dataset):

    fig = plt.figure(figsize=(8,8))

    plt.imshow(
        dataset["mask"],
        cmap="gray"
    )

    plt.title("Validity Mask")

    plt.axis("off")

    plt.colorbar()

    plt.tight_layout()

    plt.show()



def inspect_incidence(dataset):

    fig = plt.figure(figsize=(8,8))

    plt.imshow(
        dataset["incidence"],
        cmap="viridis"
    )

    plt.title("Incidence Angle")

    plt.axis("off")

    plt.colorbar()

    plt.tight_layout()

    plt.show()



def compare_hv_vh(dataset):

    hv = dataset["bands"]["HV"]

    vh = dataset["bands"]["VH"]

    diff = abs(hv.astype(float) - vh.astype(float))

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(16,5)
    )

    axes[0].imshow(
        percentile_stretch(hv),
        cmap="gray"
    )

    axes[0].set_title("HV")

    axes[0].axis("off")


    axes[1].imshow(
        percentile_stretch(vh),
        cmap="gray"
    )

    axes[1].set_title("VH")

    axes[1].axis("off")


    im = axes[2].imshow(
        diff,
        cmap="hot"
    )

    axes[2].set_title("|HV − VH|")

    axes[2].axis("off")

    plt.colorbar(
        im,
        ax=axes[2]
    )

    plt.tight_layout()

    plt.show()



def total_plot(dataset):

    inspect_raw_dataset(dataset)

    inspect_log_dataset(dataset)

    inspect_histograms(dataset)

    inspect_log_histograms(dataset)

    inspect_mask(dataset)

    inspect_incidence(dataset)

    compare_hv_vh(dataset)