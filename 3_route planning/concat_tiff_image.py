'''Concatenate GeoTIFF images while keeping the geoghraphical information'''
import rasterio
import numpy as np
from rasterio.transform import Affine

# List of file paths for the GeoTIFFs to concatenate
file_list = ['line_10.tif', 'line_11.tif']  # update with your file paths

# Open the files
src_files_to_mosaic = [rasterio.open(fp) for fp in file_list]

# Read data and metadata from the first file
first_file = src_files_to_mosaic[0]
meta = first_file.meta.copy()

# Calculate total height for all images (they should have the same width and number of bands)
total_height = sum(img.shape[0] for img in src_files_to_mosaic)

# Update metadata to reflect new image size
meta.update({"height": total_height,
             "transform": Affine(first_file.transform.a, first_file.transform.b, first_file.transform.c,
                                 first_file.transform.d, first_file.transform.e, first_file.transform.f)})

# Create an empty array, using updated metadata
mosaic = np.zeros((total_height, first_file.shape[1], first_file.count))

# Copy data from each input file into the array
height = 0
for src in src_files_to_mosaic:
    data = src.read()  # read all raster values
    data = np.transpose(data, (1, 2, 0))  # rearrange dimensions to (rows, columns, bands)
    mosaic[height:height + src.shape[0], :, :] = data
    height += src.shape[0]

# Close the original files
for src in src_files_to_mosaic:
    src.close()

# Write the result to a new file
with rasterio.open('/home_2TB/unet_transfer/images_for_stitch/QGIS/mask_tiff/concat_x_crosswalk/concat_y_crosswalk_temp/concat_4_1011_temp.tif', 'w', **meta) as dst:
    dst.write(np.transpose(mosaic, (2, 0, 1)))
