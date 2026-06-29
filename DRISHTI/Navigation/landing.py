import rasterio
import numpy as np
from scipy.ndimage import distance_transform_edt, binary_dilation

def calculate_rigorous_landing_site(slope_file, roughness_file, ice_file, output_file):
    print("--- DRISHTI Rigorous Landing Site Selector (v2.0) ---")
    
    with rasterio.open(slope_file) as src:
        slope = src.read(1)
        meta = src.meta
        pixel_size = src.res[0]
        
    with rasterio.open(roughness_file) as src:
        roughness = src.read(1)
        
    with rasterio.open(ice_file) as src:
        ice_map = src.read(1)
        
    # 1. GENERATE STRICT BOUNDARY MASK (True where genuine data exists)
    # This prevents values from bleeding into the rectangular NoData void
    valid_data_mask = (slope != -9999.0) & (roughness != -9999.0) & (ice_map != -9999.0)
    
    # 2. CRITERIA EVALUATION
    safe_slope_mask = (slope <= 10.0) & (slope >= 0.0)
    safe_roughness_mask = (roughness <= 0.3) & (roughness >= 0.0)
    not_on_surface_ice = ice_map == 0
    
    # 3. MITIGATE DILUTION ARTIFACTS
    # Dilate known hazardous slopes by 1 pixel to create an engineering safety buffer
    hazardous_slopes = (slope > 10.0) & valid_data_mask
    buffered_hazards = binary_dilation(hazardous_slopes, structure=np.ones((3,3)))
    safe_slope_buffered = ~buffered_hazards & safe_slope_mask

    # Combine all safety layers strictly inside the valid data footprint
    absolute_safe_zones = safe_slope_buffered & safe_roughness_mask & not_on_surface_ice & valid_data_mask
    
    # 4. SCIENCE ATTRACTOR FIELD FUNCTION
    print("Computing distance transforms to volatile deposits...")
    # Distance calculated from safe pixels to the nearest target ice concentration pixel
    ice_presence = (ice_map > 0) & valid_data_mask
    if not np.any(ice_presence):
        print("WARNING: No ice pixels detected inside the valid mask footprint.")
        dist_to_ice_m = np.zeros_like(slope)
    else:
        dist_to_ice_pixels = distance_transform_edt(~ice_presence)
        dist_to_ice_m = dist_to_ice_pixels * pixel_size
    
    # Exponential decay function for science prioritization
    science_score = np.exp(-dist_to_ice_m / 2000.0)
    
    # Initialize the output matrix with explicit -9999.0 NoData values
    final_landing_matrix = np.full(slope.shape, -9999.0, dtype=np.float32)
    
    # Calculate continuous scores only inside the absolute safe zones
    final_landing_matrix[absolute_safe_zones] = science_score[absolute_safe_zones]
    
    # Find global optimum coordinates strictly within safe zones
    if np.any(absolute_safe_zones):
        # Temporarily mask out NoData values to locate the max index
        search_matrix = np.where(absolute_safe_zones, science_score, -1.0)
        best_pixel = np.unravel_index(np.argmax(search_matrix), search_matrix.shape)
        
        print(f"\n[SUCCESS] Mathematically Vetted Landing Site Verified:")
        print(f"Row/Col Grid Index: {best_pixel}")
        print(f"Validated Slope at site: {slope[best_pixel]:.4f}°")
        print(f"Validated Roughness at site: {roughness[best_pixel]:.4f} meters")
        print(f"Distance to nearest ice deposit: {dist_to_ice_m[best_pixel]:.2f} meters")
        print(f"Calculated Science yield factor: {science_score[best_pixel]:.4f}")
    else:
        print("\n[CRITICAL ERROR] Zero pixels satisfied the joint constraint matrix.")
        return None
        
    # Update profile metadata to map -9999.0 as NoData
    meta.update(dtype=rasterio.float32, nodata=-9999.0, compress='lzw')
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(final_landing_matrix, 1)
        
    print(f"[FILE WRITTEN] Rigorous scoring raster exported to: {output_file}")
    return best_pixel

if __name__ == "__main__":
    calculate_rigorous_landing_site(
        slope_file=r"C:\DRISHTI_POC\FINAL_Shoemaker_Slope.tif",
        roughness_file=r"C:\DRISHTI_POC\FINAL_Shoemaker_Roughness.tif",
        ice_file=r"C:\DRISHTI_POC\DRISHTI_FINAL_ICE_MAP.tif",
        output_file=r"C:\DRISHTI_POC\FINAL_Landing_Score.tif"
    )