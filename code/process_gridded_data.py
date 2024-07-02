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
import handle_gridded_data
import pandas as pd

regions_names = ['Dakar', 
                 'Diourbel', 
                 'Fatick', 
                 'Kaffrine', 
                 'Kaolack', 
                 'Kedougou', 
                 'Kolda', 
                 'Louga', 
                 'Matam', 
                 'Saint-Louis', 
                 'Sedhiou', 
                 'Tambacounda', 
                 'Thies', 
                 'Ziguinchor']

#%% Livestock, get pixels inside regions
path_gridded_liv = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\inputs\\gridded_livestock\\"

list_files_2009 = [path_gridded_liv + "cattle\\5_Ct_2009_Da.tif",
                   path_gridded_liv + "goats\\5_Gt_2009_Da.tif",
                   path_gridded_liv + "horses\\5_Ho_2009_Da.tif",
                   path_gridded_liv + "sheep\\5_Sh_2009_Da.tif"]

list_files_2019 = [path_gridded_liv + "cattle\\5_Ct_2019_Da.tif",
                   path_gridded_liv + "goats\\5_Gt_2019_Da.tif",
                   path_gridded_liv + "horses\\5_Ho_2019_Da.tif",
                   path_gridded_liv + "sheep\\5_Sh_2019_Da.tif"]

lists_files = [list_files_2009, list_files_2019]
years = [2009, 2019]


#extract gadm country division data
_ , regions_coord = handle_gridded_data.get_regions_coord()
#all pixels
pixel_centroids, pixel_indices = handle_gridded_data.all_pixels()
#indices_inside = fetch_gadm_data.coord_inside_region(0, regions_coord, pixel_centroids)
pixel_centroids_in_regions, pixel_indices_in_regions = handle_gridded_data.coord_all_region(pixel_centroids, pixel_indices, regions_coord, pixel_centroids)
# coordinates are in [long, lat] (carefull, in google earth it's [lat,long])
del pixel_centroids, pixel_indices #these are heavy variables


#save data in good format
liv_regions_years = []

for year, list_files in zip(years, lists_files):
    liv_regions = handle_gridded_data.iterate_species(list_files, pixel_indices_in_regions, regions_names)
    liv_regions_years.append(liv_regions)
    print(liv_regions)

d = {'year': years}
for i, name in enumerate(regions_names): 
    d["liv_"+name]= [liv_regions_years[0][i], 
                     liv_regions_years[1][i]]
        
dataframe_liv = pd.DataFrame(data=d)
dataframe_liv.to_excel(path_gridded_liv + "processed_grid_2.xlsx")

get_liv = pd.read_excel(path_gridded_liv + "processed_grid_2.xlsx")

#%% Population
import tifffile
import numpy as np
from matplotlib import pyplot as plt

path_gridded_pop = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\inputs\\gridded_pop\\"
path_pop_data = path_gridded_pop + "sen_ppp_2020_1km_Aggregated_UNadj.tif"

im = tifffile.imread(path_pop_data)
#the image is in [lat, long], with lat going from up to down
imarray = np.array(im) #data in []
    
plt.imshow(imarray)
plt.show()


#%% get pixels for each region

import handle_gridded_data

_ , regions_coord_pop = handle_gridded_data.get_regions_coord()
#in [long, lat]

#all pixels
pixel_centroids_pop, pixel_indices_pop = handle_gridded_data.all_pixels_pop()
#in [latitude longitude]

pixel_centroids_in_regions, pixel_indices_in_regions = handle_gridded_data.coord_all_region(pixel_centroids_pop, pixel_indices_pop, regions_coord_pop)
# coordinates are in [long, lat] (carefull, in google earth it's [lat,long])


test = handle_gridded_data.get_pop_regions(path_pop_data, pixel_indices_in_regions, regions_names)

copy = imarray.copy()
for coord in pixel_indices_in_regions[1]:
    copy[coord]=0
plt.imshow(copy)
plt.show()