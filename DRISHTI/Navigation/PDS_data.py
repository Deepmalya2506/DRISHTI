import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os

def process_pds_to_drishti_grid(pds_label_path, reference_tif, output_tif, is_dem=True):
    print(f"--- Processing {os.path.basename(pds_label_path)} ---")
    
    # 1. Read the Reference Grid (The master 25m radar swath)
    with rasterio.open(reference_tif) as ref:
        dst_transform = ref.transform
        dst_crs = ref.crs
        dst_shape = (ref.height, ref.width)
        profile = ref.profile
        
    # 2. Open the raw PDS label
    with rasterio.open(pds_label_path) as src:
        # Read the raw data
        raw_data = src.read(1).astype(np.float32)
        
        # Apply physics scaling
        if is_dem:
            print("Applying 0.5 meter scaling factor to elevation data...")
            raw_data = raw_data * 0.5
            nodata_val = -9999.0
            resampling_method = Resampling.bilinear
        else:
            print("Processing Illumination data...")
            # PDS Illumination maps are typically scaled as percentages or fractions.
            # We normalize it to a strict 0.0 to 1.0 fraction.
            max_val = np.max(raw_data)
            if max_val > 1.0:
                raw_data = raw_data / max_val
            nodata_val = -9999.0
            resampling_method = Resampling.average
            
        # 3. Create destination array
        dst_array = np.full(dst_shape, nodata_val, dtype=np.float32)
        
        print("Warping to 25m DRISHTI Polar Stereographic grid...")
        reproject(
            source=raw_data,
            destination=dst_array,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=resampling_method
        )
        
    # 4. Save to GeoTIFF
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw',
        nodata=nodata_val
    )
    
    with rasterio.open(output_tif, 'w', **profile) as dst:
        dst.write(dst_array, 1)
        
    print(f"[SUCCESS] Wrote {output_tif}\n")

if __name__ == "__main__":
    BASE_DIR = r"C:\DRISHTI_POC"
    REFERENCE_CPR = os.path.join(BASE_DIR, "WARPED_CPR.tif")
    
    # Update these paths to where you saved the downloaded PDS files
    LDEM_LBL = r"C:\DRISHTI_POC\LDEM_85S_10M.LBL"
    ILLUM_LBL = r"C:\DRISHTI_POC\LDEM_85S_10M.IMG"
    
    # Outputs
    OUT_DEM = os.path.join(BASE_DIR, "FULL_POLAR_DEM_25m.tif")
    OUT_ILLUM = os.path.join(BASE_DIR, "FULL_POLAR_ILLUM_25m.tif")
    
    # Execute Ingestion
    process_pds_to_drishti_grid(LDEM_LBL, REFERENCE_CPR, OUT_DEM, is_dem=True)
    process_pds_to_drishti_grid(ILLUM_LBL, REFERENCE_CPR, OUT_ILLUM, is_dem=False)