''' This script should be run within the QGIS software using the built-in python console
    The program starts from the current view of the QGIS map, crops the map/annotation image based on the output_size,
    renders and saves the image in two formats: PNG and GeoTIFF. GeoTIFF format will contain all geographical data.
    This process will go from left to right, and top to bottom. For example: if the map is divided into a 10 by 10 grid,
    the program will process the image from [0][0], [0][1], [0][2],..., to [0][9], then [1][0],...,[1][9], and so on until [9][9]
    shift_distance and shift_distance_vertical is the horizontal and verical distance that the map will be shift when moving 
    to a new grid. If the shift_distance and shift_distance_vertical are the same size as the output_size, then the output 
    images will not overlap and can be used for concatenation
'''
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QImage
from osgeo import gdal

def render_and_convert():
    project = QgsProject.instance()
    map_settings = QgsMapSettings()
    map_settings.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:3857'))  # replace with your CRS
    map_settings.setLayers(project.mapLayers().values())
    output_size = QSize(1846, 882)  # adjust size
    map_settings.setOutputSize(output_size)

    current_extent = iface.mapCanvas().extent()

    # Get the coordinates of the current extent
    x_min = current_extent.xMinimum()
    y_min = current_extent.yMinimum()
    x_max = current_extent.xMaximum()
    y_max = current_extent.yMaximum()
    original_extent = QgsRectangle(x_min, y_min, x_max, y_max)

    # Define the shift distance
    shift_distance = original_extent.width()  # adjust value
    shift_distance_vertical = original_extent.height() 
    for j in range(11):
        original_extent = QgsRectangle(x_min, y_min - j * shift_distance_vertical, x_max, y_max - j * shift_distance_vertical)
        for i in range(10):
            new_extent = QgsRectangle(
                original_extent.xMinimum() + i * shift_distance,
                original_extent.yMinimum(),
                original_extent.xMaximum() + i * shift_distance,
                original_extent.yMaximum()
            )
            map_settings.setExtent(new_extent)

            render_job = QgsMapRendererParallelJob(map_settings)
            render_job.start()
            render_job.waitForFinished()

            image = render_job.renderedImage()
            temp_img_path = f"/home_2TB/unet_transfer/images_for_stitch/QGIS/image/temp_image_{j}{i}.png"  # adjust path
            image.save(temp_img_path)

            # Convert to GeoTIFF
            convert_to_geotiff(temp_img_path, f"/home_2TB/unet_transfer/images_for_stitch/QGIS/TIFF/output_{j}{i}.tif", new_extent, output_size)  # adjust output path

def convert_to_geotiff(src_filename, dst_filename, extent, img_size):
    # Open existing dataset
    src_ds = gdal.Open(src_filename)

    # Open output format driver, see gdal_translate --formats for list
    format = "GTiff"
    driver = gdal.GetDriverByName(format)

    # Output to new format
    dst_ds = driver.CreateCopy(dst_filename, src_ds, 0)

    # Calculate pixel width and height
    pixel_width = extent.width() / img_size.width()
    pixel_height = extent.height() / img_size.height()

    # Georeference the image
    geotransform = (extent.xMinimum(), pixel_width, 0, extent.yMaximum(), 0, -pixel_height)
    dst_ds.SetGeoTransform(geotransform)

    # Close the datasets
    src_ds = None
    dst_ds = None

    return

render_and_convert()