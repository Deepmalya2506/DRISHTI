import rasterio

path = r"E:\CH2_DFSAR_data\data\calibrated\20210302\ch2_sar_ncxl_20210302t162713191_d_sli_xx_fp_hh_d32.tif"

with rasterio.open(path) as src:

    print("Bands:", src.count)

    print("Dtype:", src.dtypes)

    print("Shape:", src.height, src.width)

    print("Desc:",src.descriptions)

    print("Profile",src.profile)

    print("Meta:",src.meta)