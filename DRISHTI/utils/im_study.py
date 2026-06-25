import matplotlib.pyplot as plt
import matplotlib.image as mpimg

browse_img_path=r'E:\CH2_DFSAR_data\browse\calibrated\20210302\ch2_sar_ncxl_20210302t162713191_b_brw_xx_fp_xx_d32.png'
browse = mpimg.imread(browse_img_path)
plt.figure(figsize=(8, 8))
plt.imshow(browse)
plt.title('DFSAR Browse Image — Shoemaker Region')
plt.axis('off')
plt.savefig(r'C:\Users\DEEPMALYA\Projects\DRISHTI_BAH\artifacts\data_img', dpi=150)
plt.show()

# Observation from the Image strip

""" 
The Ribbon Geometry: The twisting, segmented look of the image is the result of mapping a polar orbit track into a raw image array without complete map-projection warping (it is an unrectified browse product).

The Ring-Like Feature (Lower Center-Left): There is a distinct, circular rim structure visible about one-third of the way up from the bottom-left of the strip. This represents a smaller polar crater footprint captured inside your 10 km swath.

The Crater Floor/Rim Signature: Notice how certain semicircular features show a highly bright edge facing the direction of radar illumination (radar layover/foreshortening on steep walls) and a dark interior. That dark interior is exactly what a smooth crater floor looks like to an active radar—making it an prime candidate area to hunt for ice using your CPR and DOP pipelines.
"""
