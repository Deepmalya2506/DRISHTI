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