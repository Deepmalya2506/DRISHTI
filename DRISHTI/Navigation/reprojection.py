import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os

def warp_to_drishti_grid(source_file, master_file, output_file, resampling_method=Resampling.average):
    print(f"Warping {os.path.basename(source_file)} to DRISHTI grid...")
    
    with rasterio.open(master_file) as master:
        # Extract the exact geometry of your Phase 1 radar data
        target_transform = master.transform
        target_crs = master.crs
        target_shape = (master.height, master.width)
        # copy profile while dataset is open
        master_profile = master.profile.copy()
        
    with rasterio.open(source_file) as src:
        # Create an empty array to hold the newly aligned data
        destination_array = np.zeros(target_shape, dtype=np.float32)
        
        # Perform the mathematical warp
        reproject(
            source=rasterio.band(src, 1),
            destination=destination_array,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=target_transform,
            dst_crs=target_crs,
            resampling=resampling_method
        )
        
        # Write the aligned data to a new GeoTIFF using stored profile
        profile = master_profile
        profile.update(
            dtype=rasterio.float32,
            count=1,
            compress='lzw'
        )
        
        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(destination_array, 1)
            
    print(f"[SUCCESS] Saved aligned file: {output_file}\n")

if __name__ == "__main__":
    # --- UPDATE THIS PATH TO YOUR ACTUAL SRI FILE ---
    master_sri_path = r"e:\CH2_DFSAR_data\data\calibrated\20210302\ch2_sar_ncxl_20210302t162713191_d_sri_xx_fp_hh_d32.tif"
    
    # Input files (The 5m LOLA Data)
    dem_in = r"e:\LOLA_DEM\Shoemaker_final_adj_5mpp_surf.tif"
    slope_in = r"e:\LOLA_DEM\Shoemaker_final_adj_5mpp_slp.tif"
    roughness_proxy_in = r"e:\LOLA_DEM\Shoemaker_final_adj_5mpp_toterr.tif"
    
    # Output files (Ready for Phase 2 Pathfinding)
    dem_out = r"C:\DRISHTI_POC\WARPED_Shoemaker_DEM.tif"
    slope_out = r"C:\DRISHTI_POC\WARPED_Shoemaker_Slope.tif"
    roughness_out = r"C:\DRISHTI_POC\WARPED_Shoemaker_Roughness_Proxy.tif"
    
    # Execute the warps
    # We use 'average' for downsampling DEM/Roughness to preserve true block means
    warp_to_drishti_grid(dem_in, master_sri_path, dem_out, Resampling.average)
    warp_to_drishti_grid(slope_in, master_sri_path, slope_out, Resampling.average)
    warp_to_drishti_grid(roughness_proxy_in, master_sri_path, roughness_out, Resampling.average)
    
    print("All terrain datasets are now perfectly aligned with DRISHTI's Phase 1 Ice Map.")