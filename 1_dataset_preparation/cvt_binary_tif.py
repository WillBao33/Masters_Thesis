'''this script reads the sidewalk road annotation and convert it to binary mask (black and white)
   saves the mask images as GeoTIFF with geographical information
'''
import rasterio
import numpy as np
import cv2
import os 
from tqdm import tqdm

png_list = os.listdir('/home_2TB/unet_transfer/images_for_stitch/QGIS/TIFF') # adjust the path
png_list = [x for x in png_list if x[-3:]=='tif']

with tqdm(total=len(png_list),unit='file') as pbar:
    for png_name in png_list:
# Open the GeoTIFF
        with rasterio.open(f'/home_2TB/unet_transfer/images_for_stitch/QGIS/TIFF/{png_name}') as src: # adjust the path
            # Read the pixel data
            img = src.read()
            # Save the metadata
            meta = src.meta

        # Convert the pixel data to a numpy array
        # Transpose the axes to the order expected by OpenCV (height, width, bands)
        img = np.transpose(img, [1, 2, 0])

        # Perform image processing here...
        # For example, convert to grayscale with OpenCV
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        (thresh, im_bw) = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        invert = cv2.bitwise_not(im_bw)

        # Convert the processed data back to the original shape (bands, height, width)
        gray = np.expand_dims(invert, axis=0)

        # Update the metadata to reflect the number of bands in the processed image
        meta['count'] = gray.shape[0]

        # Write the processed data to a new GeoTIFF, preserving the metadata
        with rasterio.open(f'/home_2TB/unet_transfer/images_for_stitch/QGIS/mask_tiff/{png_name}', 'w', **meta) as dst: # adjust the path
            dst.write(gray)
