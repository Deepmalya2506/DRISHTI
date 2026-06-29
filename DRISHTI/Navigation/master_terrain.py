import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
from scipy.ndimage import uniform_filter
import os

# --- PATHS ---
# Using ONLY the valid Shoemaker surface file
SHOEMAKER_DEM_IN = r"e:\LOLA_DEM\Shoemaker_final_adj_5mpp_surf.tif"
DRISHTI_SRI = r"e:\CH2_DFSAR_data\data\calibrated\20210302\ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_hh_d32.tif"
OUT_DIR = r"C:\DRISHTI_POC"

def optimized_roughness(dem_array, window_size=7):
    """Calculates rolling standard deviation for surface roughness."""
    print("Calculating native 5m surface roughness...")
    c1 = uniform_filter(dem_array, size=window_size)
    c2 = uniform_filter(dem_array * dem_array, size=window_size)
    variance = c2 - (c1 * c1)
    return np.sqrt(np.maximum(variance, 0))

def calculate_slope(dem_array, pixel_size=5.0):
    """Calculates absolute slope in degrees."""
    print("Calculating native 5m slope...")
    dy, dx = np.gradient(dem_array, pixel_size, pixel_size)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    return np.degrees(slope_rad)

def warp_to_grid(src_array, src_transform, src_crs, master_path, out_path, resampling=Resampling.average):
    """Warps an array to the DRISHTI 25m Polar Stereographic grid."""
    print(f"Warping to 25m DRISHTI grid: {os.path.basename(out_path)}...")
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
    
    # -9999.0 ensures QGIS knows what the void space is
    profile.update(dtype=rasterio.float32, count=1, compress='lzw', nodata=-9999.0)
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(dst_array, 1)

if __name__ == "__main__":
    print("--- DRISHTI FINAL TERRAIN PIPELINE ---")
    
    # 1. Load the single, valid Shoemaker DEM
    with rasterio.open(SHOEMAKER_DEM_IN) as src:
        raw_dem = src.read(1)
        src_transform = src.transform
        src_crs = src.crs
        
    # 2. Compute physics at native 5m resolution
    slope_5m = calculate_slope(raw_dem, pixel_size=5.0)
    roughness_5m = optimized_roughness(raw_dem, window_size=7)
    
    # 3. Warp to the 25m radar grid
    warp_to_grid(raw_dem, src_transform, src_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "FINAL_Shoemaker_DEM.tif"), Resampling.average)
    warp_to_grid(slope_5m, src_transform, src_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "FINAL_Shoemaker_Slope.tif"), Resampling.average)
    
    # We use MAX resampling for roughness to preserve peak boulder heights (hazards) when downsampling
    warp_to_grid(roughness_5m, src_transform, src_crs, DRISHTI_SRI, os.path.join(OUT_DIR, "FINAL_Shoemaker_Roughness.tif"), Resampling.max)
    
    print("\n[SUCCESS] Clean terrain products generated.")