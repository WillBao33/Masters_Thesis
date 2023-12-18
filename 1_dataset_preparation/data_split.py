'''data split: train, test, and validation
   put all images inside a folder following this format: /../../input/class1/,
   then run the program will split the dataset into train/test/validation depending on the given ratio
   Do the same for the mask images
'''
import splitfolders

splitfolders.ratio('/home_2TB/Sidewalk_extraction/Dataset/input/',output="/home_2TB/Sidewalk_extraction/Dataset/output",seed=1337,ratio=(0.8,0.1,0.1))