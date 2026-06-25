import rasterio

from DRISHTI.utils.xml_parser import parse_metadata
from DRISHTI.utils.rast_explore import raster_summary
from DRISHTI.utils.stats import matrix_statistics

from DRISHTI.utils.validation import (
    check_same_shape,
    reciprocity_report,
    validate_xml_vs_raster,
    validate_mask,
    validate_incidence,
)

from DRISHTI.utils.report import dataset_report


BASE = r"E:\CH2_DFSAR_data\data\calibrated\20210302"

PREFIX = "ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_"

XML_FILE = "ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_xx_d32.xml"


def load_band(path):

    with rasterio.open(path) as src:

        arr = src.read(1)

        return (
            arr,
            src.transform,
            src.crs,
        )


def build_drishti_dataset():

    print("\nInitializing DRISHTI Dataset...\n")

    metadata = parse_metadata(
        rf"{BASE}\{XML_FILE}"
    )

    HH, transform, crs = load_band(
        rf"{BASE}\{PREFIX}hh_d32.tif"
    )

    HV, _, _ = load_band(
        rf"{BASE}\{PREFIX}hv_d32.tif"
    )

    VH, _, _ = load_band(
        rf"{BASE}\{PREFIX}vh_d32.tif"
    )

    VV, _, _ = load_band(
        rf"{BASE}\{PREFIX}vv_d32.tif"
    )

    with rasterio.open(
        rf"{BASE}\ch2_sar_ncxl_20210302t162713191_d_sri_ma_fp_xx_d32.tif"
    ) as src:

        valid_mask = src.read(1) == 1

    with rasterio.open(
        rf"{BASE}\ch2_sar_ncxl_20210302t162713191_d_sri_in_fp_xx_d32.tif"
    ) as src:

        incidence = src.read(1)

    bands = {

        "HH": HH,

        "HV": HV,

        "VH": VH,

        "VV": VV,

    }

    summary = raster_summary(
        rf"{BASE}\{PREFIX}hh_d32.tif"
    )

    check_same_shape(bands)

    validate_xml_vs_raster(
        metadata,
        summary,
    )

    validate_mask(
        valid_mask,
        HH,
    )

    validate_incidence(
        incidence,
        HH,
    )

    band_stats = {}

    for name, band in bands.items():

        band_stats[name] = matrix_statistics(
            band
        )

    reciprocity = reciprocity_report(
        HV,
        VH,
    )

    dataset_report(
        metadata,
        summary,
        band_stats,
        reciprocity,
    )

    dataset = {

        "bands": bands,

        "mask": valid_mask,

        "incidence": incidence,

        "transform": transform,

        "crs": crs,

        "metadata": metadata,

    }

    return dataset


if __name__ == "__main__":

    dataset = build_drishti_dataset()