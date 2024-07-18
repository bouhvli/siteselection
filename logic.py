import os
import numpy as np
from osgeo import gdal, ogr
import matplotlib.pyplot as plt
from functions import get_extent, shapefile_to_raster, calculate_proximity, reclassify_raster,read_raster, write_raster

# data = all the criteria given by the user
data = []
# output_dir = the out put file where the files and folders will be created
output_dir = ''
# resolution = also will be given by the user 
resolution = ''
# Calculate the extent from the essaouira shapefile
study_area = 'shapefile/location'

extent = get_extent(study_area)
xmin, xmax, ymin, ymax = extent

# Iterate over each shapefile and convert to raster
raster_dir = os.path.join(output_dir, 'rasterise')
os.makedirs(raster_dir, exist_ok=True)
for shapefile in data:
    base_name = os.path.basename(shapefile).replace('.shp', '.tif')
    output_path = os.path.join(raster_dir, base_name)
    shapefile_to_raster(shapefile, output_path, xmin, xmax, ymin, ymax, resolution)

print("Conversion completed successfully.")

proximity_dir = os.path.join(output_dir, 'proximity')
os.makedirs(proximity_dir, exist_ok=True)

rasterized_criterion = []

# Iterate over each raster and calculate proximity
for raster in rasterized_criterion:
    base_name = os.path.basename(raster)
    proximity_path = os.path.join(proximity_dir, "prox_" + base_name)

    # Calculate proximity
    calculate_proximity(raster, proximity_path)

print("Proximity calculation completed successfully.")

proximited_criterion = []

reclass_schemes = {}

reclass_dir = os.path.join(output_dir, 'reclassify')
os.makedirs(reclass_dir, exist_ok=True)

for raster in proximited_criterion:
    base_name = os.path.basename(raster)
    reclass_scheme_key = os.path.splitext(base_name)[0]
    reclass_scheme = reclass_schemes[reclass_scheme_key]
    reclass_path = os.path.join(reclass_dir, "reclass_" + base_name)

    # Reclassify raster
    reclassify_raster(raster, reclass_path, reclass_scheme)

print("Reclassification completed successfully.")

reclassified_criterion = []

weights = {}


# loop through the layers and read the reclassified layers 
# criterion extracting the criteria array with the reference dataset 
study_area_array, ref_dataset = read_raster(study_area)

overlay_layers = (""" adding criteria with it's equivlant weight""") * study_area_array

output_path = os.path.join(output_dir, "suitability_map.tif")

write_raster(output_path, overlay_layers, ref_dataset)

fresult_map, dataset = read_raster(output_path)

# Mask out the non-data values (0 to 1)
fresult_map[fresult_map < 1] = np.nan

# Plot the suitability map
plt.figure(figsize=(10, 8))
plt.imshow(fresult_map, cmap="viridis")
plt.colorbar(label="Suitability Score")
plt.title("Suitability Map")
plt.axis("off")
plt.savefig()