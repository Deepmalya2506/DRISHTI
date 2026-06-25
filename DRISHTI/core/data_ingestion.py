import rasterio
import numpy as np
import xml.etree.ElementTree as ET

BASE = r"E:\CH2_DFSAR_data\data\calibrated\20210302"
PREFIX = "ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_"

def build_drishti_dataset(base_path, prefix):
    print("=== [DRISHTI] Initializing Ingestion Pipeline ===")
    
    # ─── 1. PARSE METADATA DESCRIPTORS ──────────────────────────────────────
    xml_path = rf"{base_path}\{prefix}xx_d32.xml"
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Simple recursive finder for structural parameters
    def find_tag_value(element, target_tag):
        tag_clean = element.tag.split('}')[-1]
        if tag_clean == target_tag:
            return element.text
        for child in element:
            res = find_tag_value(child, target_tag)
            if res is not None:
                return res
        return None

    k_c = float(find_tag_value(root, "calibration_constant"))           #type: ignore
    az_looks = float(find_tag_value(root, "azimuth_looks"))             #type:ignore
    rg_looks = float(find_tag_value(root, "range_looks"))               #type:ignore
    spacing = float(find_tag_value(root, "output_pixel_spacing"))       #type:ignore
    
    spatial_metadata = {
        "calibration_constant": k_c,
        "looks": az_looks * rg_looks,
        "pixel_spacing": spacing
    }
    
    # ─── 2. DETACHED DATA INGESTION (RAW DN) ─────────────────────────────────
    def load_raw_matrix(pol):
        t_path = f"{base_path}\\{prefix}{pol}_d32.tif"
        with rasterio.open(t_path) as src:
            matrix = src.read(1)
            if pol == 'hh':
                return matrix, src.transform, src.crs, src.meta['dtype']
            return matrix, None, None, src.meta['dtype']

    dn_HH, transform, crs, dtype_HH = load_raw_matrix('hh')
    dn_HV, _, _, _ = load_raw_matrix('hv')
    dn_VH, _, _, _ = load_raw_matrix('vh')
    dn_VV, _, _, _ = load_raw_matrix('vv')
    
    # Load Ancillary Maps
    with rasterio.open(f"{base_path}\\{prefix}ma_fp_xx_d32.tif") as src:
        valid_mask = (src.read(1) == 1)
        
    with rasterio.open(f"{base_path}\\{prefix}in_fp_xx_d32.tif") as src:
        incidence_map = src.read(1).astype(np.float64)

    # Update spatial metadata with coregistration variables
    spatial_metadata["transform"] = transform #type: ignore
    spatial_metadata["crs"] = crs #type: ignore

    # Assemble Structural Object
    dataset = {
        "raw_dn": {"HH": dn_HH, "HV": dn_HV, "VH": dn_VH, "VV": dn_VV},
        "calibrated_sigma0": {"HH": None, "HV": None, "VH": None, "VV": None},
        "ancillary": {"mask": valid_mask, "incidence": incidence_map},
        "spatial_metadata": spatial_metadata
    }
    
    # ─── 3. DATA VALIDATION & METRIC REPORTING (STEP 3) ──────────────────────
    print("\n--- Pipeline Validation Metrics ---")
    bands = dataset["raw_dn"]
    
    # Shape and Boundary Structural Assertions
    ref_shape = dn_HH.shape
    for b_name, b_matrix in bands.items():
        print(f"Band {b_name:2s} | Dtype: {b_matrix.dtype} | Shape: {b_matrix.shape} | Max DN: {b_matrix.max()}")
        assert b_matrix.shape == ref_shape, f"Catastrophic Shape Mismatch in Band {b_name}"
    
    assert dtype_HH == 'uint16', f"Expected UnsignedLSB2 (uint16), got {dtype_HH}"
    
    # Quantify Reciprocity Imbalances
    raw_hv_f = dn_HV.astype(np.float64)
    raw_vh_f = dn_VH.astype(np.float64)
    reciprocity_delta = raw_hv_f - raw_vh_f
    
    rmse_recip = np.sqrt(np.mean(reciprocity_delta ** 2))
    mean_bias = np.mean(reciprocity_delta)
    
    print(f"\n[Reciprocity Evaluation]")
    print(f"  Cross-Pol Raw RMSE:  {rmse_recip:.4f} DN")
    print(f"  Cross-Pol Mean Bias: {mean_bias:.4f} DN")
    
    return dataset #dict

# Execution block for your E: drive footprint
dataset = build_drishti_dataset(BASE, PREFIX)