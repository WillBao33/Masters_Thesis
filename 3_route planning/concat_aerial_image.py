'''This script concatenates all aerial images from the dataset horizontally and vertically to construt the city-scale aerial map'''
import cv2
import numpy as np

def concatenate_images_horizontally(image_list):
    return cv2.hconcat(image_list)

def concatenate_images_vertically(image_list):
    return cv2.vconcat(image_list)

if __name__ == "__main__":
    # Initialize an empty list to store the vertically concatenated images
    vertical_concatenated_images = []
    
    # Loop through sets of 10 images
    for i in range(0, 110, 10):
        # Initialize an empty list to store the 10 images to concatenate horizontally
        horizontal_images = []
        
        # Load each of the 10 images and append them to the list
        for j in range(i, i + 10):
            image_name = f"temp_image_{j:02d}.png" # adjust the image path
            img = cv2.imread(image_name)
            horizontal_images.append(img)
        
        # Perform horizontal concatenation
        concatenated_horizontal_img = concatenate_images_horizontally(horizontal_images)
        
        # Append the horizontally concatenated image to the vertical list
        vertical_concatenated_images.append(concatenated_horizontal_img)
    
    # Perform vertical concatenation of all horizontally concatenated images
    final_image = concatenate_images_vertically(vertical_concatenated_images)
    
    # Save the final concatenated image
    cv2.imwrite("final_concatenated_image.png", final_image) # adjust the output path

