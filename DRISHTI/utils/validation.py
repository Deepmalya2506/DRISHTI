import numpy as np


def check_same_shape(bands):

    shapes = [b.shape for b in bands.values()]

    first = shapes[0]

    for s in shapes:

        if s != first:

            raise ValueError(
                f"Shape mismatch {first} vs {s}"
            )
        
def reciprocity_report(HV, VH):

    hv = HV.astype(float)

    vh = VH.astype(float)

    delta = hv - vh

    rmse = np.sqrt(np.mean(delta**2))

    corr = np.corrcoef(
        hv.ravel(),
        vh.ravel()
    )[0,1]

    return {

        "rmse": rmse,

        "correlation": corr,

        "bias": np.mean(delta)

    }