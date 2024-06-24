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

import os
os.chdir(path_code)
import fetch_gadm_data

#extract gadm country division data
regions_names, regions_coord = fetch_gadm_data.get_regions_coord()
#all pixels
pixel_centroids, pixel_indices = fetch_gadm_data.all_pixels()
#indices_inside = fetch_gadm_data.coord_inside_region(0, regions_coord, pixel_centroids)
pixel_centroids_in_regions, pixel_indices_in_regions = fetch_gadm_data.coord_all_region(pixel_centroids, pixel_indices, regions_coord, pixel_centroids)

        