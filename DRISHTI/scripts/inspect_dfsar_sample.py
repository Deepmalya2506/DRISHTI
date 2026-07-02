import os
import numpy as np
import rasterio

BASE = r"E:\CH2_DFSAR_data\data\calibrated\20210302"
PREFIX = "ch2_sar_ncxl_20210302t162713191_d_sli_xx_fp_"

FILES = {
    "HH": os.path.join(BASE, PREFIX + "hh_d32.tif"),
    "HV": os.path.join(BASE, PREFIX + "hv_d32.tif"),
    "VH": os.path.join(BASE, PREFIX + "vh_d32.tif"),
    "VV": os.path.join(BASE, PREFIX + "vv_d32.tif"),
}


def inspect_sample(row0=0, col0=0, height=64, width=64):
    print("Inspecting DFSAR sample windows from the real calibrated data...\n")

    for name, path in FILES.items():
        if not os.path.exists(path):
            print(f"[MISSING] {name}: {path}")
            continue

        with rasterio.open(path) as src:
            arr = src.read(1)
            sample = arr[row0:row0 + height, col0:col0 + width]

            print(f"{name}: {path}")
            print(f"  shape: {arr.shape}")
            print(f"  dtype: {arr.dtype}")
            print(f"  sample_min: {sample.min():.3f}")
            print(f"  sample_max: {sample.max():.3f}")
            print(f"  sample_mean: {sample.mean():.3f}")
            print(f"  sample_std: {sample.std():.3f}")
            print(f"  sample_window:\n{sample[:8, :8]}")
            print()


if __name__ == "__main__":
    inspect_sample()
