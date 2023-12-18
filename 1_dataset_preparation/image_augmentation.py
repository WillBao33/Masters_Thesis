'''image augmentation: horizontal and vertical flip (PNG only)'''
from PIL import Image
import os
from tqdm import tqdm

png_list = os.listdir('/home_2TB/new_sidewalk/crop_image') # adjust the path
png_list = [x for x in png_list if x[-3:]=='png']

with tqdm(total=len(png_list),unit='file') as pbar:

    for png_name in png_list:
        #if shp_name[:-4] in jp2_list[:-4]:
        original_img = Image.open(f'/home_2TB/new_sidewalk/crop_image/{png_name}') # adjust the path
        original_mask = Image.open(f'/home_2TB/new_sidewalk/binary_mask/{png_name}') # adjust the path
        vertical_img = original_img.transpose(method=Image.FLIP_TOP_BOTTOM)
        vertical_mask = original_mask.transpose(method=Image.FLIP_TOP_BOTTOM)
        horz_img = original_img.transpose(method=Image.FLIP_LEFT_RIGHT)
        horz_mask = original_mask.transpose(method=Image.FLIP_LEFT_RIGHT)
        original_img.save(f"/home_2TB/new_sidewalk/image/{png_name}.png") # adjust the path
        original_mask.save(f"/home_2TB/new_sidewalk/mask/{png_name}.png") # adjust the path
        vertical_img.save(f"/home_2TB/new_sidewalk/image/{png_name}_vf.png",quality=95) # adjust the path
        vertical_mask.save(f"/home_2TB/new_sidewalk/mask/{png_name}_vf.png",quality=95) # adjust the path
        horz_img.save(f"/home_2TB/new_sidewalk/image/{png_name}_hf.png",quality=95) # adjust the path
        horz_mask.save(f"/home_2TB/new_sidewalk/mask/{png_name}_hf.png",quality=95) # adjust the path

        pbar.update()
# open the original image
# original_img = Image.open("/home/will/Pictures/image.png")
# original_mask = Image.open("/home/will/Pictures/mask.png")
# vertical_img = original_img.transpose(method=Image.FLIP_TOP_BOTTOM)
# vertical_mask = original_mask.transpose(method=Image.FLIP_TOP_BOTTOM)
# horz_img = original_img.transpose(method=Image.FLIP_LEFT_RIGHT)
# horz_mask = original_mask.transpose(method=Image.FLIP_LEFT_RIGHT)
# vertical_img.save("/home/will/Pictures/image_vf.png",quality=95)
# vertical_mask.save("/home/will/Pictures/mask_vf.png",quality=95)
# horz_img.save("/home/will/Pictures/image_hf.png",quality=95)
# horz_mask.save("/home/will/Pictures/mask_hf.png",quality=95)

