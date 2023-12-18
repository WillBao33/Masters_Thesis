'''crosswalk annotation using line function'''
import cv2 

image = cv2.imread('/home_2TB/unet_transfer/images_for_stitch/mask/17.png', cv2.IMREAD_COLOR)

path = cv2.line(image, (103,827), (184, 800), (255,255,255), 8) # width,height
path = cv2.line(path, (779, 226), (838, 208), (255,255,255), 5)
path = cv2.line(path, (884, 583), (961, 560), (255,255,255), 5)
path = cv2.line(path, (1796, 398), (1772, 315), (255,255,255), 5)

cv2.imwrite('/home_2TB/unet_transfer/images_for_stitch/paper/planning/mask/mask_17.png',path)