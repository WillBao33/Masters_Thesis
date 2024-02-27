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
2. Follow the video instructions to create the sidewalk annotations:
   * This method can also create segmentation annotations for other classes, such as roads, road boundaries, and buildings.
   * Select different coordinate systems and scales based on application preference.
3. Under the [1_dataset_preparation](./1_dataset_preparation) directory, execute the [Export_image.py](./1_dataset_preparation/Export_image.py) **inside** the QGIS software built-in Python console.
