import matplotlib.pyplot as plt
import numpy as np


def show_image(
    image,
    title="",
    cmap="gray",
    figsize=(8,8),
    colorbar=True,
    vmin=None,
    vmax=None
):

    plt.figure(figsize=figsize)

    plt.imshow(
        image,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax
    )

    plt.title(title)

    plt.axis("off")

    if colorbar:
        plt.colorbar()

    plt.tight_layout()

    plt.show()

def show_histogram(
    image,
    title="Histogram",
    bins=200,
    log=False
):

    arr = image.ravel()

    arr = arr[np.isfinite(arr)]

    plt.figure(figsize=(8,4))

    plt.hist(
        arr,
        bins=bins
    )

    if log:
        plt.yscale("log")

    plt.title(title)

    plt.xlabel("Pixel Value")

    plt.ylabel("Frequency")

    plt.tight_layout()

    plt.show()

def percentile_stretch(
    image,
    low=2,
    high=98
):

    p_low = np.percentile(image, low)

    p_high = np.percentile(image, high)

    return np.clip(image, p_low, p_high)

def log_scale(image):

    image = image.astype(np.float64)

    return np.log10(image + 1)

def rgb_composite(r,g,b):

    rgb = np.dstack([r,g,b])

    rgb -= rgb.min()

    rgb /= rgb.max()

    return rgb