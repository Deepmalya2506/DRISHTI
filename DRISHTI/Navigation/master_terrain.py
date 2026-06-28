import rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling
import numpy as np
from scipy.ndimage import uniform_filter
import glob
import os

# --- PATHS ---
LOLA_DIR = r"e:\LOLA_DEM"
DRISHTI_SRI = r"e:\CH2_DFSAR_data\data\calibrated\20210302\ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_hh_d32.tif"
OUT_DIR = r"C:\DRISHTI_POC"

def optimized_roughness(dem_array, window_size=7):
    """Calculates rolling standard deviation extremely fast."""
    print("Calculating native 5m surface roughness...")
    c1 = uniform_filter(dem_array, size=window_size)
    c2 = uniform_filter(dem_array * dem_array, size=window_size)
    variance = c2 - (c1 * c1)
    # Ensure no negative variance due to floating point inaccuracies
    return np.sqrt(np.maximum(variance, 0))

def calculate_slope(dem_array, pixel_size=5.0):
    """Calculates slope in degrees using central differences."""
    print("Calculating native 5m slope...")
    dy, dx = np.gradient(dem_array, pixel_size, pixel_size)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    return np.degrees(slope_rad)

def warp_to_grid(src_array, src_transform, src_crs, master_path, out_path, resampling=Resampling.average):
    """Warps an array in memory to the DRISHTI 25m grid."""
    print(f"Warping to 25m grid: {os.path.basename(out_path)}...")
    with rasterio.open(master_path) as master:
        dst_transform = master.transform
        dst_crs = master.crs
        dst_shape = (master.height, master.width)
        profile = master.profile
        
    dst_array = np.zeros(dst_shape, dtype=np.float32)
    
    reproject(
        source=src_array,
        destination=dst_array,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=dst_transform,
        dst_crs=dst_crs,
        resampling=resampling
    )
    
    profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=-9999.0)
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(dst_array, 1)

if __name__ == "__main__":
    print("--- DRISHTI NATIVE RESOLUTION PIPELINE ---")
    
    # 1. FIND ALL 5m SURF TILES
    search_criteria = os.path.join(LOLA_DIR, "*_surf.tif")
    dem_files = glob.glob(search_criteria)
    
    # 2. SEAMLESS MERGE
    print(f"Merging {len(dem_files)} LOLA tiles to eliminate seams...")
    src_files_to_mosaic = []
    for fp in dem_files:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)
        
    merged_dem, merged_transform = merge(src_files_to_mosaic)
    merged_dem = merged_dem[0] # Extract 2D array
    merged_crs = src_files_to_mosaic[0].crs
    
    # Close source files
    for src in src_files_to_mosaic: src.close()
    
    # 3. COMPUTE PHYSICS AT NATIVE 5M
    slope_5m = calculate_slope(merged_dem, pixel_size=5.0)
    roughness_5m = optimized_roughness(merged_dem, window_size=7) # 35mx35m physical window
    
    # 4. WARP EVERYTHING TO 25M
    warp_to_grid(merged_dem, merged_transform, merged_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "WARPED_CLEAN_DEM.tif"), Resampling.average)
    warp_to_grid(slope_5m, merged_transform, merged_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "WARPED_CLEAN_Slope.tif"), Resampling.average)
    # Use Resampling.max for roughness so we don't lose the highest boulders during downsampling!
    warp_to_grid(roughness_5m, merged_transform, merged_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "WARPED_CLEAN_Roughness.tif"), Resampling.max)
    
    print("\n[SUCCESS] Pipeline Complete. No seams. True roughness preserved.")