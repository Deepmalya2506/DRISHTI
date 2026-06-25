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

import numpy as np


def validate_xml_vs_raster(metadata: dict, raster_summary: dict):
    """
    Compare XML metadata against raster metadata.
    Raises ValueError if inconsistencies are found.
    """

    xml_height = int(metadata["no_scans"])
    xml_width = int(metadata["no_pixels"])

    raster_height, raster_width = raster_summary["shape"]

    if xml_height != raster_height:
        raise ValueError(
            f"Height mismatch: XML={xml_height}, Raster={raster_height}"
        )

    if xml_width != raster_width:
        raise ValueError(
            f"Width mismatch: XML={xml_width}, Raster={raster_width}"
        )

    xml_dtype = metadata["data_type"]

    if raster_summary["dtype"] != "uint16":
        raise ValueError(
            f"Unexpected raster dtype {raster_summary['dtype']}"
        )

    if xml_dtype != "UnsignedLSB2":
        raise ValueError(
            f"Unexpected XML datatype {xml_dtype}"
        )

    return True


def validate_mask(mask, reference):

    if mask.shape != reference.shape:
        raise ValueError(
            "Validity mask shape mismatch."
        )

    return True


def validate_incidence(incidence, reference):

    if incidence.shape != reference.shape:
        raise ValueError(
            "Incidence map shape mismatch."
        )

    return True