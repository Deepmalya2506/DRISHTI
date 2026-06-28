import rasterio
import numpy as np
from scipy.ndimage import distance_transform_edt
import os

def calculate_landing_scores(slope_file, roughness_file, ice_file, output_file):
    print("--- Initializing DRISHTI Landing Site Selector ---")
    
    with rasterio.open(slope_file) as src:
        slope = src.read(1)
        meta = src.meta
        pixel_size = src.res[0] # 25 meters
        
    with rasterio.open(roughness_file) as src:
        roughness = src.read(1)
        
    with rasterio.open(ice_file) as src:
        ice_map = src.read(1)
        
    # 1. HARD CONSTRAINTS (The Vikram Lander Limits)
    # Slope must be < 10 degrees. 
    # Roughness proxy (Total Z uncertainty) must be low (e.g., < 0.3 meters variance)
    # Cannot land directly on the ice target (often inside PSRs / unstable)
    
    safe_slope = slope <= 10.0
    safe_roughness = roughness <= 0.3
    not_on_ice = ice_map == 0
    
    valid_landing_zones = safe_slope & safe_roughness & not_on_ice
    
    # 2. PROXIMITY SCORING (Science Return)
    print("Calculating distance to primary ice targets...")
    # Distance transform gives distance to nearest 0. We invert the ice map so ice = 0.
    dist_to_ice_pixels = distance_transform_edt(ice_map == 0)
    dist_to_ice_m = dist_to_ice_pixels * pixel_size
    
    # We want to be close, but not INSIDE the crater. 
    # Let's say optimal distance is 500m to 2000m from the ice boundary.
    # Score decays exponentially the further we get from the ice.
    science_score = np.exp(-dist_to_ice_m / 2000.0)
    
    # 3. COMBINED SCORING
    # Apply the valid zone mask to the score
    final_score = valid_landing_zones.astype(np.float32) * science_score
    
    # Find the absolute best pixel
    best_pixel = np.unravel_index(np.argmax(final_score), final_score.shape)
    best_score = final_score[best_pixel]
    
    print(f"\n[SUCCESS] Optimal Landing Site Found!")
    print(f"Row/Col Index: {best_pixel}")
    print(f"Slope at site: {slope[best_pixel]:.2f} degrees")
    print(f"Roughness Z-Error at site: {roughness[best_pixel]:.2f} meters")
    print(f"Distance to nearest ice: {dist_to_ice_m[best_pixel]:.2f} meters")
    
    # Write the score map for visualization in QGIS
    meta.update(dtype=rasterio.float32)
    with rasterio.open(output_file, 'w', **meta) as dst:
        dst.write(final_score, 1)
        
    print(f"\nSaved Landing Score Map to: {output_file}")
    return best_pixel

if __name__ == "__main__":
    # Input Paths
    slope_in = r"C:\DRISHTI_POC\WARPED_Shoemaker_Slope.tif"
    roughness_in = r"C:\DRISHTI_POC\WARPED_Shoemaker_Roughness_Proxy.tif"
    ice_in = r"C:\DRISHTI_POC\DRISHTI_FINAL_ICE_MAP.tif" # Update if named differently
    
    # Output Path
    score_out = r"C:\DRISHTI_POC\WARPED_Landing_Score.tif"
    
    target = calculate_landing_scores(slope_in, roughness_in, ice_in, score_out)