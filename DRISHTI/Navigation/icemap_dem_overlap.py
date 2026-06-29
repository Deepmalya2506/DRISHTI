import rasterio
import numpy as np
from scipy.ndimage import (distance_transform_edt, binary_dilation, 
                            binary_erosion, label, maximum_filter)
import subprocess, os

NODATA = -9999.0
BASE = r"C:\DRISHTI_POC"

# ============================================================
# PHASE A: VERIFY SPATIAL OVERLAP BEFORE ANY COMPUTATION
# This diagnostic must be run FIRST — it tells you whether 
# your data layers actually intersect geographically.
# ============================================================

def spatial_overlap_audit():
    """
    Prints the geographic bounds of every key layer.
    If bounds don't overlap, nothing downstream will work.
    """
    files = {
        "ICE_MAP":   f"{BASE}/DRISHTI_FINAL_ICE_MAP.tif",
        "SLOPE":     f"{BASE}/FINAL_Shoemaker_Slope.tif", 
        "ROUGHNESS": f"{BASE}/FINAL_Shoemaker_Roughness.tif",
        "DEM":       f"{BASE}/FINAL_Shoemaker_DEM.tif",
        "CPR":       f"{BASE}/WARPED_CPR.tif",  # Reference grid
    }
    
    print("=" * 70)
    print("SPATIAL OVERLAP AUDIT")
    print("=" * 70)
    
    bounds_list = {}
    for name, fpath in files.items():
        if not os.path.exists(fpath):
            print(f"{name:12s}: FILE NOT FOUND — {fpath}")
            continue
        with rasterio.open(fpath) as src:
            b = src.bounds
            bounds_list[name] = b
            nodata_val = src.nodata
            arr = src.read(1)
            valid_count = np.sum(arr != nodata_val) if nodata_val else np.sum(~np.isnan(arr))
            print(f"\n{name}")
            print(f"  Bounds: left={b.left:.1f}, right={b.right:.1f}, "
                  f"bottom={b.bottom:.1f}, top={b.top:.1f}")
            print(f"  Size: {src.width} × {src.height} pixels @ {abs(src.transform.a):.1f}m")
            print(f"  CRS:  {src.crs}")
            print(f"  Nodata declared: {nodata_val}")
            print(f"  Valid pixels: {valid_count:,} / {arr.size:,} "
                  f"({100*valid_count/arr.size:.2f}%)")
            
            # Check how many ice pixels fall within DEM footprint
            if name == "ICE_MAP":
                ice_pixels = np.sum(arr > 0)
                print(f"  Ice pixels (value > 0): {ice_pixels:,}")
    
    # Check pairwise overlap of ICE_MAP vs DEM
    if "ICE_MAP" in bounds_list and "DEM" in bounds_list:
        bi = bounds_list["ICE_MAP"]
        bd = bounds_list["DEM"]
        overlap_left  = max(bi.left,   bd.left)
        overlap_right = min(bi.right,  bd.right)
        overlap_bottom= max(bi.bottom, bd.bottom)
        overlap_top   = min(bi.top,    bd.top)
        
        if overlap_left < overlap_right and overlap_bottom < overlap_top:
            overlap_w = overlap_right  - overlap_left
            overlap_h = overlap_top    - overlap_bottom
            print(f"\n✅ ICE_MAP ∩ DEM overlap: {overlap_w/1000:.1f} km × "
                  f"{overlap_h/1000:.1f} km")
        else:
            print("\n❌ CRITICAL: ICE_MAP and DEM DO NOT SPATIALLY OVERLAP.")
            print("   This is why zero pixels pass all constraints.")
            print("   ACTION: Download LDEM_85S_5M.IMG from NASA PDS.")

# Run this FIRST
spatial_overlap_audit()


# ============================================================
# PHASE B: WARP FULL POLAR DEM TO DFSAR GRID
# Only run after downloading LDEM_85S_5M.IMG
# ============================================================

def warp_polar_dem_to_sri_grid(polar_dem_img, reference_cpr_tif, output_tif):
    """
    Warps the full south polar LOLA DEM to exactly match the DFSAR grid.
    Uses the CPR raster as the authoritative spatial reference.
    """
    with rasterio.open(reference_cpr_tif) as ref:
        ref_bounds = ref.bounds
        ref_crs = ref.crs.to_wkt()
        ref_res = ref.res
    
    print(f"Reference grid: {ref.width}×{ref.height} @ {ref_res[0]}m")
    print(f"Bounds: {ref_bounds}")
    
    cmd = [
        "gdalwarp",
        "-r", "bilinear",
        "-tr", str(ref_res[0]), str(ref_res[1]),
        "-te", str(ref_bounds.left), str(ref_bounds.bottom),
              str(ref_bounds.right), str(ref_bounds.top),
        "-t_srs", ref_crs,
        "-dstnodata", str(NODATA),
        "-of", "GTiff",
        "-co", "COMPRESS=LZW",
        "-co", "TILED=YES",
        polar_dem_img,
        output_tif
    ]
    
    print("Running gdalwarp for full polar DEM...")
    subprocess.run(cmd, check=True)
    print(f"[WRITTEN] {output_tif}")
    
    # Verify
    with rasterio.open(output_tif) as dst:
        arr = dst.read(1)
        valid = arr != NODATA
        print(f"Warped DEM valid pixels: {np.sum(valid):,} / {arr.size:,}")
        print(f"Elevation range: {arr[valid].min():.1f}m to {arr[valid].max():.1f}m")


# ============================================================
# PHASE C: RECOMPUTE SLOPE AND ROUGHNESS ON FULL POLAR DEM
# After warp_polar_dem_to_sri_grid produces FINAL_POLAR_DEM.tif
# ============================================================

def compute_slope_and_roughness_from_full_dem(dem_tif, output_slope, output_roughness):
    """
    Computes slope (degrees) and roughness proxy from the full polar DEM.
    Roughness = rolling std at native scale before downsampling is already
    baked into the 5m→25m warp via bilinear; compute additional local std
    at 3×3 window on the 25m grid for the cost map.
    """
    with rasterio.open(dem_tif) as src:
        dem = src.read(1).astype(np.float64)
        pixel_m = abs(src.transform.a)
        meta = src.meta.copy()
    
    valid = dem != NODATA
    dem_nan = np.where(valid, dem, np.nan)
    
    # Slope via central difference
    dy, dx = np.gradient(dem_nan, pixel_m, pixel_m)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)
    
    # Roughness: local elevation std in 5×5 window (125m at 25m/px)
    from scipy.ndimage import generic_filter
    roughness = generic_filter(
        dem_nan, 
        lambda x: np.nanstd(x), 
        size=5, 
        mode='constant', 
        cval=np.nan
    )
    
    # Report physical range
    s_valid = slope_deg[valid]
    r_valid = roughness[valid]
    print(f"Slope range: {np.nanmin(s_valid):.2f}° – {np.nanmax(s_valid):.2f}°")
    print(f"Roughness range: {np.nanmin(r_valid):.2f}m – {np.nanmax(r_valid):.2f}m")
    print(f"Pixels with slope ≤ 10°: {np.sum(s_valid <= 10):,}")
    print(f"Pixels with roughness ≤ 5m: {np.sum(r_valid <= 5):,}")
    
    out = np.where(valid, slope_deg, NODATA).astype(np.float32)
    meta.update(dtype='float32', nodata=NODATA, compress='lzw')
    with rasterio.open(output_slope, 'w', **meta) as dst:
        dst.write(out, 1)
    
    out = np.where(valid, roughness, NODATA).astype(np.float32)
    with rasterio.open(output_roughness, 'w', **meta) as dst:
        dst.write(out, 1)
    
    print(f"[WRITTEN] {output_slope}")
    print(f"[WRITTEN] {output_roughness}")


# ============================================================
# PHASE D: LANDING SCORE WITH RELAXED, PHYSICALLY GROUNDED CONSTRAINTS
# ============================================================

def compute_landing_score_v4(slope_file, roughness_file, ice_file, dem_file,
                              illumination_file=None, output_file=None):
    """
    v4: Relaxed constraints grounded in actual Vikram/Pragyan specs.
    
    Constraint changes from v3:
    - slope_buffer reduced from 2px to 1px (25m, not 50m)
    - roughness threshold raised to 8m (25m-pixel std dev proxy, not 0.35m)
      because 0.35m was an OHRC-resolution metric, not 25m-DEM metric
    - lambda_ice raised to 5000m (Pragyan-class rover realistic traverse)
    - illumination gate added if file available
    """
    
    SLOPE_MAX = 10.0        # degrees, Vikram hard limit
    ROUGH_MAX = 8.0         # meters, std dev at 25m scale (not OHRC scale)
    SLOPE_BUFFER_PX = 1     # 1 pixel = 25m buffer, not 50m
    LAMBDA_ICE_M = 5000.0   # Pragyan realistic traverse range
    ILLUM_MIN = 0.30        # 30% annual illumination for solar survival
    
    print("=" * 65)
    print("DRISHTI Landing Site Selector v4.0")
    print(f"Constraints: slope≤{SLOPE_MAX}°, rough≤{ROUGH_MAX}m, "
          f"illum≥{ILLUM_MIN if illumination_file else 'N/A'}")
    print("=" * 65)
    
    # Load all layers
    def load(fpath):
        with rasterio.open(fpath) as src:
            arr = src.read(1).astype(np.float32)
            arr[arr == src.nodata] = np.nan if src.nodata else arr
            return arr, src.meta.copy(), abs(src.transform.a)
    
    slope,     meta, px = load(slope_file)
    roughness, _,   _  = load(roughness_file)
    ice,       _,   _  = load(ice_file)
    dem,       _,   _  = load(dem_file)
    
    footprint = ~np.isnan(slope) & ~np.isnan(roughness) & ~np.isnan(dem)
    
    print(f"\nValid footprint pixels: {np.sum(footprint):,}")
    print(f"Slope ≤ {SLOPE_MAX}°:  "
          f"{np.sum((slope <= SLOPE_MAX) & footprint):,}")
    print(f"Roughness ≤ {ROUGH_MAX}m: "
          f"{np.sum((roughness <= ROUGH_MAX) & footprint):,}")
    
    # Safety gates
    cond_slope = (slope <= SLOPE_MAX) & footprint
    
    hazardous = (slope > SLOPE_MAX) & footprint
    buffered_hazards = binary_dilation(hazardous, 
                                        structure=np.ones((3,3)),
                                        iterations=SLOPE_BUFFER_PX)
    cond_slope_safe = cond_slope & ~buffered_hazards
    cond_roughness  = (roughness <= ROUGH_MAX) & footprint
    cond_not_on_ice = np.where(np.isnan(ice), True, ice == 0) & footprint
    
    A = cond_slope_safe & cond_roughness & cond_not_on_ice
    
    # Illumination gate (optional)
    if illumination_file and os.path.exists(illumination_file):
        illum, _, _ = load(illumination_file)
        cond_illum = (illum >= ILLUM_MIN) & footprint
        A = A & cond_illum
        print(f"Illumination ≥ {ILLUM_MIN}: "
              f"{np.sum(cond_illum & footprint):,}")
    else:
        print("Illumination: NOT APPLIED (file not provided)")
        print("  → Download ILLUM_SP_85S from PDS before final presentation")
    
    print(f"\nPixels after slope gate:     {np.sum(cond_slope_safe):,}")
    print(f"Pixels after roughness gate: {np.sum(cond_slope_safe & cond_roughness):,}")
    print(f"TOTAL admissible pixels:     {np.sum(A):,}")
    
    if np.sum(A) == 0:
        print("\n[CRITICAL] Still zero pixels. Diagnostic breakdown:")
        print(f"  Slope only (≤{SLOPE_MAX}°):         {np.sum(cond_slope):,}")
        print(f"  After slope buffer:            {np.sum(cond_slope_safe):,}")
        print(f"  Roughness only (≤{ROUGH_MAX}m):       {np.sum(cond_roughness):,}")
        print(f"  Slope ∩ Roughness:             "
              f"{np.sum(cond_slope_safe & cond_roughness):,}")
        print(f"  Not on ice:                    {np.sum(cond_not_on_ice):,}")
        print(f"  All three ∩:                   {np.sum(A):,}")
        print("\nACTION REQUIRED: The DEM footprint likely doesn't contain")
        print("ice pixels. Run spatial_overlap_audit() first.")
        return None
    
    # Science attractor
    ice_presence = (~np.isnan(ice)) & (ice > 0) & footprint
    dist_px = distance_transform_edt(~ice_presence)
    dist_m  = dist_px * px
    science  = np.exp(-dist_m / LAMBDA_ICE_M)
    
    final_score = np.full(slope.shape, NODATA, dtype=np.float32)
    final_score[A] = science[A]
    
    # Optimal site
    search = np.where(A, science, -1.0)
    best = np.unravel_index(np.argmax(search), search.shape)
    
    print(f"\n{'='*65}")
    print("OPTIMAL LANDING SITE — DRISHTI v4.0")
    print(f"{'='*65}")
    print(f"Grid (row, col):      {best}")
    print(f"DEM elevation:        {dem[best]:.1f} m")
    print(f"Slope:                {slope[best]:.3f}°")
    print(f"Roughness:            {roughness[best]:.3f} m")
    print(f"Distance to ice:      {dist_m[best]:.0f} m")
    print(f"Science score:        {science[best]:.4f}")
    
    if slope[best] < 0.1 and roughness[best] < 0.01:
        print("\n⚠ WARNING: slope and roughness still suspiciously near zero.")
        print("  Run spatial_overlap_audit() — DEM footprint may not")
        print("  overlap ice pixels. LDEM_85S_5M.IMG is required.")
    
    if output_file:
        meta.update(dtype='float32', nodata=NODATA, compress='lzw')
        with rasterio.open(output_file, 'w', **meta) as dst:
            dst.write(final_score, 1)
        print(f"\n[WRITTEN] {output_file}")
    
    return best


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    
    # STEP 1 — Always run this first
    spatial_overlap_audit()
    
    # STEP 2 — Only after downloading LDEM_85S_5M.IMG:
    # warp_polar_dem_to_sri_grid(
    #     polar_dem_img = r"E:\LOLA_DEM\LDEM_85S_5M.IMG",
    #     reference_cpr_tif = f"{BASE}/WARPED_CPR.tif",
    #     output_tif = f"{BASE}/FULL_POLAR_DEM_25m.tif"
    # )
    
    # STEP 3 — After warp:
    # compute_slope_and_roughness_from_full_dem(
    #     dem_tif        = f"{BASE}/FULL_POLAR_DEM_25m.tif",
    #     output_slope   = f"{BASE}/FULL_POLAR_Slope_25m.tif",
    #     output_roughness = f"{BASE}/FULL_POLAR_Roughness_25m.tif"
    # )
    
    # STEP 4 — Landing score on full grid:
    # compute_landing_score_v4(
    #     slope_file     = f"{BASE}/FULL_POLAR_Slope_25m.tif",
    #     roughness_file = f"{BASE}/FULL_POLAR_Roughness_25m.tif",
    #     ice_file       = f"{BASE}/DRISHTI_FINAL_ICE_MAP.tif",
    #     dem_file       = f"{BASE}/FULL_POLAR_DEM_25m.tif",
    #     illumination_file = f"{BASE}/ILLUM_SP_85S.tif",  # when available
    #     output_file    = f"{BASE}/FINAL_Landing_Score_v4.tif"
    # )