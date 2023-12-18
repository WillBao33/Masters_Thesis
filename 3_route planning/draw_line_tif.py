'''crosswalk annotation on GeoTIFF image with line function
   crosswalk annotation is in gray color
'''
import rasterio
import cv2
import numpy as np

# Open your GeoTIFF
with rasterio.open('/home_2TB/unet_transfer/images_for_stitch/QGIS/mask_tiff/concat_x_crosswalk/concat_y_crosswalk_temp/concat_3_6789_temp.tif') as dataset: # adjust the path
    # read the image data
    array = dataset.read(1)
    
    # Convert array to an 8-bit array for cv2 operations
    cv2_array = np.uint8(array)

    # Draw a line using cv2.line()
    # start_point = (100, 100)  # These are pixel coordinates
    # end_point = (200, 200)
    # color = (255, 0, 0)  # RGB color
    # thickness = 2  # Line thickness in pixels
    path = cv2.line(cv2_array, (8090,1775), (8169,1751), 128, 8)
    path = cv2.line(path, (8188,1761), (8211,1834), 128, 8)
    path = cv2.line(path, (12812,2604), (12849,2751), 128, 8)
    path = cv2.line(path, (12987,2535), (13036,2673), 128, 8)

    # Save the image as GeoTIFF using rasterio
    with rasterio.open('/home_2TB/unet_transfer/images_for_stitch/QGIS/mask_tiff/concat_x_crosswalk/concat_y_crosswalk_final/concat_3_6789.tif', 'w', driver='GTiff', 
                       height=path.shape[0], width=path.shape[1], 
                       count=1, dtype=str(path.dtype), crs=dataset.crs, 
                       transform=dataset.transform) as dst:
        dst.write(path, 1)
