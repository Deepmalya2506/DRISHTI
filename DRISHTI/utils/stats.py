import numpy as np


def matrix_statistics(arr):

    arr = arr.astype(np.float64)

    return {

        "min": np.nanmin(arr),

        "max": np.nanmax(arr),

        "mean": np.nanmean(arr),

        "median": np.nanmedian(arr),

        "std": np.nanstd(arr),

    }