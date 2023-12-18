'''sidewalk extraction refinement with A* path planning algorithm'''
from astar.search import AStar
import numpy as np 
from PIL import Image
import cv2

# Make a map (any size!)
world = np.zeros((896,1856))
#image = cv2.imread('/home_2TB/unet_transfer/images_for_stitch/concat_mask/concat_skel.png',cv2.IMREAD_UNCHANGED)
#invert = cv2.bitwise_not(image)
#print(invert/255)
#world = np.array(invert/255).astype(int)
# print(invert[835,1173])
# print(invert[271,1532])
#print(world)
# world = [
#     [0,0,0],
#     [1,1,0],
#     [0,0,0],
#     ]
#print(world)
# define a start and end goals (x, y) (vertical, horizontal)
start = (96,1797) # height,width
goal = (68,1820)

# # search
path = AStar(world).search(start, goal)
# path = np.array(path)
# print(path.shape)
mask = np.array(Image.open('/home_2TB/unet_transfer/images_for_stitch/paper/overlay_14.png').convert("RGB")) # path for prediction need to be refined
for i in path:
   mask[i[0],i[1]] = [255,0,0]

Image.fromarray(mask).save(f'/home_2TB/unet_transfer/images_for_stitch/paper/final_14.png', quality=95) # output refined image

#         # if (mask[i,j] != [92, 54, 229]).all() and (mask[i,j] != [255, 127, 0]).all() and (mask[i,j] != [255,255,255]).all():
#         #     mask[i,j] = [92, 54, 229]
#         if (mask[i,j] != [255,0,0]).all() and (mask[i,j] != [255, 127, 0]).all() and (mask[i,j] != [0,255,0]).all():
#             mask[i,j] = [255,127,0]

