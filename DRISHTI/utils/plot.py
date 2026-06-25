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