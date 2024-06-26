# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:46:03 2024

@author: anem

Extract region from the GeoJSON region files in folder '1'.
Put them into 'regions' folder with county subfolders with the same name as their region.
In these subfolders also put a file with the list of regions ('regions.txt').
"""

path = path_repository = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated"
path_code = path + "\\code"

import numpy as np
import os
os.chdir(path_code)
import handle_gridded_data, core, input_fetch
from matplotlib import pyplot as plt
import tifffile 

#extract gadm country division data
regions_names, regions_coord = handle_gridded_data.get_regions_coord()
#all pixels
pixel_centroids, pixel_indices = handle_gridded_data.all_pixels()
#indices_inside = fetch_gadm_data.coord_inside_region(0, regions_coord, pixel_centroids)
pixel_centroids_in_regions, pixel_indices_in_regions = handle_gridded_data.coord_all_region(pixel_centroids, pixel_indices, regions_coord, pixel_centroids)
# coordinates are in [long, lat] (carefull, in google earth it's [lat,long])
del pixel_centroids, pixel_indices

#%%
path_gridded = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\inputs\\gridded_livestock\\"

list_files_2009 = [path_gridded + "cattle\\5_Ct_2009_Da.tif",
                   path_gridded + "goats\\5_Gt_2009_Da.tif",
                   path_gridded + "horses\\5_Ho_2009_Da.tif",
                   path_gridded + "sheep\\5_Sh_2009_Da.tif"]

list_files_2019 = [path_gridded + "cattle\\5_Ct_2019_Da.tif",
                   path_gridded + "goats\\5_Gt_2019_Da.tif",
                   path_gridded + "horses\\5_Ho_2019_Da.tif",
                   path_gridded + "sheep\\5_Sh_2019_Da.tif"]

lists_files = [list_files_2009, list_files_2019]
years = [2009, 2019]

for year, list_files in zip(years, lists_files):
    liv = iterate_species(list_files, pixel_indices_in_regions, regions_names)

def iterate_species(list_files, pixel_indices_in_regions, regions_names):
    livetock_species = [] #in order: cattle, goats, horse and sheep
    for path in list_files:
        livetock_species.append(get_livestock_regions(path, pixel_indices_in_regions, regions_names))
    print(livetock_species)
    liv = input_fetch.calculate_liv(0, livetock_species[0], livetock_species[2], 
                                    0, livetock_species[1], livetock_species[3])
    return liv

def get_livestock_regions(path, pixel_indices_in_regions, regions_names):
    im = tifffile.imread(path)
    #the image is in [lat, long], with lat going from up to down
    imarray = np.array(im) #data in []
    
    livestock_regions = []
    for r in range(len(regions_names)):
        livestock_region = []
        for coordinates in pixel_indices_in_regions[r]:
            coordinates = [2160-coordinates[1], coordinates[0]]
            livestock_region.append(imarray[coordinates[0], coordinates[1]])
        livestock_region = core.remove_values_under_thres(livestock_region, 0)
        livestock_regions.append(sum(livestock_region))
    
    #livestock_regions = [sum(livestock_region) for livestock_region in livestock_regions]
    return livestock_regions