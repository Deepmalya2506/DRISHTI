# MIDAS Output Extraction — CMD Script

This script converts raw `.bin` files from MIDAS into `.tif` format for use in Python.

```bat
cd C:\MidasV4.2.4
call EnvSet.bat

set ML=C:\DRISHTI_POC\midas_output\ch2_sar_ncxl_20210302t162713191_d_fp_d32_Process\L_Band

:: 1. Core Stokes & CPR
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\stokes\ML\cpr.bin" "C:\DRISHTI_POC\1_CPR_MIDAS_slant.tif"
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\stokes\ML\s3.bin"  "C:\DRISHTI_POC\2_S3_MIDAS_slant.tif"

:: 2. Filtered T3 Matrix (For Python DOP & Power)
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\T11.bin" "C:\DRISHTI_POC\3_T11_FILT_slant.tif"
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\T22.bin" "C:\DRISHTI_POC\4_T22_FILT_slant.tif"
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\T33.bin" "C:\DRISHTI_POC\5_T33_FILT_slant.tif"
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\T12_Real.bin" "C:\DRISHTI_POC\6_T12_Real_FILT_slant.tif"

:: 3. Yamaguchi Physical Structures (For Hazard Mapping)
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\Yamaguchi_Y4R\YM4_even.bin" "C:\DRISHTI_POC\7_YAMA_DoubleBounce_Hazard_slant.tif"
gdal\bin\gdal\apps\gdal_translate -of GTiff -ot Float32 "%ML%\T3\T3_FILT\Yamaguchi_Y4R\YM4_vol.bin"  "C:\DRISHTI_POC\8_YAMA_Volume_Ice_slant.tif"
```

---

Terminal Window
![Terminal Window](images\cmd.png)