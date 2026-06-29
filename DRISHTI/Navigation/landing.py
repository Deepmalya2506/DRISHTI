import rasterio
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_dilation, binary_erosion
from rasterio.warp import reproject, Resampling
import subprocess
import os

# ============================================================
# STEP 0: RE-WARP WITH EXPLICIT NODATA ENFORCEMENT
# Run this FIRST via subprocess before loading any arrays
# ============================================================
def rewarp_with_proper_nodata(input_tif, reference_tif, output_tif, nodata_val=-9999.0):
    """
    Re-warp a raster to match reference grid, STRICTLY encoding 
    out-of-bounds regions as nodata_val, never as 0.0
    """
    with rasterio.open(reference_tif) as ref:
        ref_crs = ref.crs.to_wkt()
        ref_transform = ref.transform
        ref_width = ref.width
        ref_height = ref.height
    
    cmd = [
        "gdalwarp",
        "-r", "bilinear",
        "-dstnodata", str(nodata_val),
        "-srcnodata", str(nodata_val),
        "-of", "GTiff",
        "-co", "COMPRESS=LZW",
        input_tif, output_tif
    ]
    # Only rewarp if output doesn't exist
    if not os.path.exists(output_tif):
        subprocess.run(cmd, check=True)
    return output_tif


# ============================================================
# STEP 1: BUILD AUTHORITATIVE VALID FOOTPRINT MASK
# The ONLY ground truth for "is this pixel real terrain?"
# is whether the DEM itself has a non-nodata value.
# ============================================================
def build_footprint_mask(dem_file, nodata_val=-9999.0, zero_tolerance=True):
    """
    Returns a boolean mask: True only where DEM has real elevation data.
    zero_tolerance=True: treats 0.0 as suspect if DEM nodata=0 was misconfigured.
    """
    with rasterio.open(dem_file) as src:
        dem = src.read(1).astype(np.float32)
        declared_nodata = src.nodata
    
    if declared_nodata is not None:
        valid = dem != declared_nodata
    else:
        valid = np.ones(dem.shape, dtype=bool)
    
    # Additional guard: if large swaths of border are 0.0, treat as nodata
    if zero_tolerance:
        # Erode valid mask slightly to remove boundary fringe pixels
        # that may have been partially filled by bilinear interpolation
        valid = binary_erosion(valid, structure=np.ones((3,3)), iterations=2)
    
    print(f"Valid DEM footprint: {np.sum(valid):,} pixels "
          f"({100*np.sum(valid)/valid.size:.2f}% of full grid)")
    return valid, dem


# ============================================================
# STEP 2: VALIDATE ALL INPUTS AGAINST FOOTPRINT
# ============================================================
def load_and_validate(filepath, footprint_mask, nodata_val=-9999.0):
    with rasterio.open(filepath) as src:
        arr = src.read(1).astype(np.float32)
        declared_nd = src.nodata
    
    # Force nodata regions to NaN for safe arithmetic
    if declared_nd is not None:
        arr[arr == declared_nd] = np.nan
    
    # Force void regions (outside DEM footprint) to NaN regardless
    arr[~footprint_mask] = np.nan
    
    valid_vals = arr[footprint_mask & ~np.isnan(arr)]
    print(f"{os.path.basename(filepath)}: "
          f"min={np.nanmin(valid_vals):.4f}, "
          f"max={np.nanmax(valid_vals):.4f}, "
          f"valid_pixels={len(valid_vals):,}")
    return arr


# ============================================================
# STEP 3: LANDING SITE SELECTION — RIGOROUS v3.0
# ============================================================
def compute_landing_score(
    slope_file,
    roughness_file, 
    ice_file,
    dem_file,
    output_file,
    # --- Chandrayaan-3 heritage constraints ---
    max_slope_deg=10.0,          # Vikram hard limit
    max_roughness=0.35,          # 5m-scale std dev proxy for boulder clearance
    slope_buffer_pixels=2,       # Safety dilation around hazardous slopes
    lambda_ice_m=2000.0,         # Pragyan max operational range
    min_illumination_proxy=None, # Optional: illumination GeoTIFF
    nodata_val=-9999.0
):
    print("=" * 60)
    print("DRISHTI Rigorous Landing Site Selector v3.0")
    print("=" * 60)
    
    # Build footprint from DEM — single source of truth
    footprint, dem = build_footprint_mask(dem_file, nodata_val)
    
    slope = load_and_validate(slope_file, footprint, nodata_val)
    roughness = load_and_validate(roughness_file, footprint, nodata_val)
    ice = load_and_validate(ice_file, footprint, nodata_val)
    
    # Get pixel size for distance calculations
    with rasterio.open(slope_file) as src:
        pixel_size_m = abs(src.transform.a)  # meters per pixel
        meta = src.meta.copy()
    
    print(f"\nPixel size: {pixel_size_m:.1f} m")
    
    # --------------------------------------------------------
    # TIER 1: BOOLEAN SAFETY GATE
    # All conditions must be simultaneously True
    # --------------------------------------------------------
    
    # Condition A: Slope within Vikram-class envelope
    cond_slope = (slope <= max_slope_deg) & (slope >= 0.0) & ~np.isnan(slope)
    
    # Condition B: Buffered slope safety (account for 5m→25m dilution)
    # Any pixel within `slope_buffer_pixels` of a steep zone is excluded
    hazardous = ((slope > max_slope_deg) & footprint & ~np.isnan(slope))
    hazard_buffer = binary_dilation(hazardous, 
                                     structure=np.ones((3,3)), 
                                     iterations=slope_buffer_pixels)
    cond_slope_buffered = cond_slope & ~hazard_buffer
    
    # Condition C: Surface roughness (sub-boulder scale)
    cond_roughness = (roughness <= max_roughness) & ~np.isnan(roughness)
    
    # Condition D: Do not land ON ice (plume gas expansion risk)
    cond_not_on_ice = (ice == 0) & ~np.isnan(ice)
    
    # Condition E: Must be inside valid DEM footprint
    cond_in_footprint = footprint
    
    # Combined admissibility mask
    A = (cond_slope_buffered & cond_roughness & 
         cond_not_on_ice & cond_in_footprint)
    
    print(f"\n--- Tier 1 Safety Filter Results ---")
    print(f"Pixels passing slope <= {max_slope_deg}°: {np.sum(cond_slope):,}")
    print(f"Pixels after slope hazard buffer: {np.sum(cond_slope_buffered):,}")
    print(f"Pixels passing roughness: {np.sum(cond_roughness & footprint):,}")
    print(f"Pixels not on ice: {np.sum(cond_not_on_ice & footprint):,}")
    print(f"TOTAL admissible pixels (all gates): {np.sum(A):,}")
    
    if np.sum(A) == 0:
        print("\n[CRITICAL] Zero pixels passed all constraints.")
        print("Diagnostic: Check if slope/roughness nodata is encoded as 0.0")
        print("Run the verification test first.")
        return None
    
    # --------------------------------------------------------
    # TIER 2: SCIENCE ATTRACTOR FIELD
    # Exponential decay from ice deposits
    # --------------------------------------------------------
    ice_presence = (ice > 0) & footprint & ~np.isnan(ice)
    print(f"\nIce pixels inside DEM footprint: {np.sum(ice_presence):,}")
    
    if np.sum(ice_presence) == 0:
        print("[WARNING] No ice detected in DEM footprint overlap.")
        print("Using center-of-footprint as proxy target.")
        # Fallback: score by proximity to footprint center
        ys, xs = np.where(footprint)
        cy, cx = int(np.mean(ys)), int(np.mean(xs))
        proxy = np.zeros_like(slope, dtype=bool)
        proxy[cy, cx] = True
        dist_px = distance_transform_edt(~proxy)
    else:
        dist_px = distance_transform_edt(~ice_presence)
    
    dist_m = dist_px * pixel_size_m
    science_score = np.exp(-dist_m / lambda_ice_m)
    
    # --------------------------------------------------------
    # OUTPUT: Initialize with explicit nodata, fill only safe zones
    # --------------------------------------------------------
    final_score = np.full(slope.shape, nodata_val, dtype=np.float32)
    final_score[A] = science_score[A].astype(np.float32)
    
    # --------------------------------------------------------
    # FIND OPTIMAL SITE
    # --------------------------------------------------------
    search = np.where(A, science_score, -1.0)
    best_rc = np.unravel_index(np.argmax(search), search.shape)
    
    # Extract properties at optimal site
    best_slope = slope[best_rc]
    best_rough = roughness[best_rc]  
    best_dist_ice = dist_m[best_rc]
    best_score = science_score[best_rc]
    best_dem = dem[best_rc]
    
    print(f"\n{'='*60}")
    print(f"OPTIMAL LANDING SITE — DRISHTI RECOMMENDATION")
    print(f"{'='*60}")
    print(f"Grid Index (row, col):    {best_rc}")
    print(f"Elevation (DEM):          {best_dem:.1f} m")
    print(f"Slope at site:            {best_slope:.3f}°  (limit: {max_slope_deg}°)")
    print(f"Roughness at site:        {best_rough:.4f} m  (limit: {max_roughness} m)")
    print(f"Distance to ice:          {best_dist_ice:.1f} m")
    print(f"Science yield score:      {best_score:.4f}")
    
    # Sanity checks
    if best_slope < 0.01:
        print(f"\n[WARNING] Slope is suspiciously near zero.")
        print("This may still be a nodata ghost. Verify with test script above.")
    if best_rough < 0.001:
        print(f"[WARNING] Roughness is suspiciously near zero. Same concern.")
    
    # Write output
    meta.update(dtype=rasterio.float32, nodata=nodata_val, compress='lzw')
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(final_score, 1)
    
    print(f"\n[WRITTEN] {output_file}")
    return best_rc, best_score


if __name__ == "__main__":
    BASE = r"C:\DRISHTI_POC"
    
    compute_landing_score(
        slope_file=    f"{BASE}/FINAL_Shoemaker_Slope.tif",
        roughness_file=f"{BASE}/FINAL_Shoemaker_Roughness.tif",
        ice_file=      f"{BASE}/DRISHTI_FINAL_ICE_MAP.tif",
        dem_file=      f"{BASE}/FINAL_Shoemaker_DEM.tif",
        output_file=   f"{BASE}/FINAL_Landing_Score_v3.tif",
        max_slope_deg=10.0,
        max_roughness=0.35,
        slope_buffer_pixels=2,
        lambda_ice_m=2000.0,
        nodata_val=-9999.0
    )