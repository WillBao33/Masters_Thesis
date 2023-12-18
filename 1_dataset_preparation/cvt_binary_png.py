# this script reads the sidewalk road annotation and convert it to binary mask (black and white)
import cv2
import os
from tqdm import tqdm


png_list = os.listdir('/home_2TB/unet_transfer/images_for_stitch/temp_mask') # adjust the annotation image path
png_list = [x for x in png_list if x[-3:]=='png']

with tqdm(total=len(png_list),unit='file') as pbar:
    for png_name in png_list:
        #if shp_name[:-4] in jp2_list[:-4]:
        im_gray = cv2.imread(f'/home_2TB/unet_transfer/images_for_stitch/temp_mask/{png_name}',cv2.IMREAD_GRAYSCALE) # adjust the annotation image path
        (thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        invert = cv2.bitwise_not(im_bw)
        #resized_up = cv2.resize(invert, (5000,5000), interpolation= cv2.INTER_LINEAR)
        cv2.imwrite(f'/home_2TB/unet_transfer/images_for_stitch/temp_mask/{png_name}',invert) # adjust the output path
        pbar.update()

# im_gray = cv2.imread('/home_2TB/Sidewalk_extraction/Dataset/mask_1.png',cv2.IMREAD_GRAYSCALE)

# (thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# #cv2.imwrite('binary.png',im_bw)

# invert = cv2.bitwise_not(im_bw)
# cv2.imwrite('/home_2TB/Sidewalk_extraction/Dataset/test_binary.png',invert)