import pandas as pd

def check_ohrc_coverage(csv_path):
    print("--- Checking OHRC Spatial Bounds ---")
    
    try:
        # The XML defines 4 fields. We extract just Longitude (col 0) and Latitude (col 1).
        # We use header=None to ensure we don't accidentally drop the first data row.
        df = pd.read_csv(csv_path, header=None, usecols=[0, 1], names=['Longitude', 'Latitude'])

        # Ensure coordinates are numeric (coerce non-numeric -> NaN)
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

        # Drop rows that do not have numeric coordinates
        valid = df.dropna(subset=['Latitude', 'Longitude'])
        if valid.empty:
            raise ValueError('No numeric Longitude/Latitude values found in CSV')

        min_lat, max_lat = valid['Latitude'].min(), valid['Latitude'].max()
        min_lon, max_lon = valid['Longitude'].min(), valid['Longitude'].max()

        print(f"OHRC Latitude Extent:  {min_lat:.4f}° to {max_lat:.4f}°")
        print(f"OHRC Longitude Extent: {min_lon:.4f}° to {max_lon:.4f}°")
        
        # DRISHTI Phase 1 approximate target coordinates
        target_lat = -87.6401
        target_lon = 44.3128
        
        # Proximity Check
        lat_match = min_lat <= target_lat <= max_lat
        lon_match = min_lon <= target_lon <= max_lon
        
        if lat_match and lon_match:
            print("\n[SUCCESS] The OHRC strip directly overlaps with the DRISHTI target center!")
        else:
            print(f"\n[INFO] The OHRC strip does not cover the exact DRISHTI center ({target_lat}, {target_lon}).")
            print("Action: Proceed to use this file to build and validate the GLCM roughness pipeline.")
            
    except Exception as e:
        print(f"Error reading CSV: {e}")

# Point this to your actual extracted file path
ohrc_csv = r"e:\OHRC\geometry\calibrated\20250111\ch2_ohr_ncp_20250111T2003456733_g_grd_d18.csv"
check_ohrc_coverage(ohrc_csv)