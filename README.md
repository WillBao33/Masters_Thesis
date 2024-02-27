# Thesis Title: Sidewalk Extraction Using Deep Learning & Cost-based Route Optimization with Mini-max Objective Function
The thesis's full text can be downloaded at https://ir.library.ontariotechu.ca/handle/10155/1707
## STATEMENT OF CONTRIBUTIONS
* Part of the work described in Chapter 2 has been published as:

Z. Bao, S. Hossain, H. Lang, and X. Lin, “A review of high-definition map creation
methods for autonomous driving,” Eng Appl Artif Intell, vol. 122, p. 106125, Jun.
2023, doi: 10.1016/J.ENGAPPAI.2023.106125.

* Part of the work described in Chapter 3 has been published as:
  
Z. Bao, H. Lang, and X. Lin, “Deep Learning-Based Sidewalk Extraction on Aerial
Image,” Proceedings of the Canadian Society for Mechanical Engineering International
Congress (CSME 2023)

* Part of the work described in Chapter 4 is being reviewed for publication as:
  
Z. Bao, H. Lang, and X. Lin, “Sidewalk Extraction on Aerial Images with Deep
Learning and Path Planning Algorithm,” Eng Appl Artif Intell.

**NOTE: sidewalk dataset available upon request**

## 1. Sidewalk Dataset Preparation
1. Download the [QGIS](https://qgis.org/en/site/) to manually create sidewalk annotations on satellite images.
2. Follow the video [instructions](https://drive.google.com/file/d/1ATnFS2TrF31PhgAlhtcCfu6uByudOMQq/view?usp=sharing) to create the sidewalk annotations:
   * This method can also create segmentation annotations for other classes, such as roads, road boundaries, and buildings.
   * Select different coordinate systems and scales based on application preference.
3. Under the [1_dataset_preparation](./1_dataset_preparation) directory, execute the [Export_image.py](./1_dataset_preparation/Export_image.py) **inside** the QGIS software built-in Python console.
   * Make sure to update your coordinate reference system (CRS), output image path, and output image format.
   * Uncheck the annotation layer when only exporting the aerial images, and vice versa when only exporting the annotation images.
4. Depending on the image format used, [cvt_binary_png.py](./1_dataset_preparation/cvt_binary_png.py) or [cvt_binary_tif.py](./1_dataset_preparation/cvt_binary_tif.py) can be used to convert the 3-channel annotation images into binary image format.
   * [cvt_binary_tif.py](./1_dataset_preparation/cvt_binary_tif.py) is suggested to be used only when the GPS information is required during the conversion.
5. [image_augmentation.py](./1_dataset_preparation/image_augmentation.py) can be used to create vertical and horizontal flip augmentation on the aerial and mask images. (optional)
6. Run [data_split.py](./1_dataset_preparation/data_split.py) to split the dataset into train/test/val sets.

## 2. Sidewalk Extraction and Refinement
1. Update the [label_class_dict.csv](./2_Sidewalk_extraction_refinement/label_class_dict.csv) based on the training classes and their corresponding pixel values.
2. Run [train.py](./2_Sidewalk_extraction_refinement/train.py) to train a segmentation model using the prepared dataset.
3. The [refinement_path_planning.py](./2_Sidewalk_extraction_refinement/refinement_path_planning.py) file will refine a broken segmentation prediction using the A* algorithm.
   * Make sure to update the graph size, the locations of two/more broken points, as well as the input and output directories.
4. The [overlay.py](./2_Sidewalk_extraction_refinement/overlay.py) file will place the refined segmentation on top of the corresponding image.

## 3. GPS-based Route Planning
1. To concatenate all aerial/mask/prediction images, run:
```
python3 concat_aerial_image.py
python3 concat_tiff_image.py
```
2. To connect the crosswalks on the map, run:
```
python3 draw_line.py
python3 draw_line_tif.py
```
3. Run GPS-based route planning on the aerial map:
```
python3 path_networkx_center_new.py
```
