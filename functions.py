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


def calculate_proximity(input_raster, output_raster):
    # Open the input raster
    src_ds = gdal.Open(input_raster)

    # Create the output raster
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(output_raster, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjectionRef())

    # Compute proximity
    gdal.ComputeProximity(src_ds.GetRasterBand(1), dst_ds.GetRasterBand(1), ["DISTUNITS=GEO"])

    # Close the datasets
    src_ds = None
    dst_ds = None


def reclassify_raster(input_raster, output_raster, reclass_scheme):
    # Open the input raster
    src_ds = gdal.Open(input_raster)
    src_band = src_ds.GetRasterBand(1)
    src_array = src_band.ReadAsArray()

    # Create the output raster
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(output_raster, src_ds.RasterXSize, src_ds.RasterYSize, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(src_ds.GetGeoTransform())
    dst_ds.SetProjection(src_ds.GetProjectionRef())
    dst_band = dst_ds.GetRasterBand(1)

    # Initialize the output array with zeros
    reclass_array = np.zeros_like(src_array, dtype=np.uint8)

    # Apply reclassification scheme
    for (low, high, value) in reclass_scheme:
        mask = np.logical_and(src_array >= low, src_array < high)
        reclass_array[mask] = value

    # Write the reclassified array to the output raster
    dst_band.WriteArray(reclass_array)

    # Close the datasets
    src_ds = None
    dst_ds = None


# Function to read raster as array
def read_raster(raster_path):
    dataset = gdal.Open(raster_path)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    return array, dataset

# Function to write array to raster
def write_raster(output_path, array, reference_dataset):
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_path, reference_dataset.RasterXSize, reference_dataset.RasterYSize, 1, gdal.GDT_Float32)
    out_dataset.SetGeoTransform(reference_dataset.GetGeoTransform())
    out_dataset.SetProjection(reference_dataset.GetProjection())
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(array)
    out_band.SetNoDataValue(-9999)
    out_dataset.FlushCache()