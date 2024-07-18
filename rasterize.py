import os
import numpy as np
from osgeo import gdal, ogr
import matplotlib.pyplot as plt


def get_extent(shapefile):
    ds = ogr.Open(shapefile)
    layer = ds.GetLayer()
    extent = layer.GetExtent()
    ds = None
    return extent

# Convert shapefiles to raster
def shapefile_to_raster(shapefile, output_path, xmin, xmax, ymin, ymax, resolution):
    # Open the shapefile
    source_ds = ogr.Open(shapefile)
    source_layer = source_ds.GetLayer()

    # Create the destination raster dataset
    x_res = int((xmax - xmin) / resolution)
    y_res = int((ymax - ymin) / resolution)
    target_ds = gdal.GetDriverByName('GTiff').Create(output_path, x_res, y_res, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((xmin, resolution, 0, ymax, 0, -resolution))

    # Set the projection from the source shapefile
    target_ds.SetProjection(source_layer.GetSpatialRef().ExportToWkt())

    # Rasterize the shapefile layer to the destination raster
    gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])

    # Close the datasets
    source_ds = None
    target_ds = None
"""
for shapefile in data:
    base_name = os.path.basename(shapefile).replace('.shp', '.tif')
    output_path = os.path.join(output_dir, base_name)
    shapefile_to_raster(shapefile, output_path, xmin, xmax, ymin, ymax, resolution)

print("Conversion completed successfully.")
"""