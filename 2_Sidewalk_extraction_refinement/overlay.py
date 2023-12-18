'''overlay the sidewalk annotation on the corresponding aerial image'''
import cv2
from PIL import Image

mask = cv2.imread("/home_2TB/unet_transfer/images_for_stitch/paper/planning/mask/mask_17.png")
height, width, _ = mask.shape

image = cv2.imread("/home_2TB/unet_transfer/images_for_stitch/image/17.png")

for i in range(height):
    for j in range(width):
        if mask[i,j].sum() != 0:
            #image[i,j] = mask[i,j]
            image[i,j] = [255,255,0]
        else: pass

Image.fromarray(image[:,:,::-1]).save('/home_2TB/unet_transfer/images_for_stitch/paper/planning/overlay/overlay_17.png',quality=95)