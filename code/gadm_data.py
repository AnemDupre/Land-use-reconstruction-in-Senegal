# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 14:46:03 2024

@author: anem

Extract region from the GeoJSON region files in folder '1'.
Put them into 'regions' folder with county subfolders with the same name as their region.
In these subfolders also put a file with the list of regions ('regions.txt').
"""

path = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\geography\\"

import json
import os
os.chdir("C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\geography\\")

    
file = path + "gadm41_SEN_1.json"
regions_names = []
coordinates = []

with open(file) as original_region_file:
    data = json.load(original_region_file)
    
    for feature in data['features']:
        # for keyword search make sure to use lowercase, unidecoded etc.
        region_name = str(feature['properties']['NAME_1'])
        region_coord = feature['geometry']['coordinates']
        
        # make sure text is lowercase, trimmed string with only alphanumeric characters
        #region_name = re.sub(r"(\w)([A-Z])", r"\1 \2", region_name).strip().lower()  # split camelcase, afterwards strip and lowercase
        #region_name = re.sub(r'[^a-z0-9 ]+', '', region_name)  # lower alphanumeric characters only
        #region_name = re.sub(r'\s+', ' ', region_name)  # remove multiple spaces and put a space in front to be able to find if keyword is at beginning of text

        regions_names.append(region_name)
        coordinates.append(region_coord)
        
# Matplotlib mplPath
import matplotlib.path as mpltPath

polygon = coordinates[3][0][0]
points = [[-17.4329, 14.6849], [-17.2946, 14.4506 ], [-15.1848, 14.1912]]
#points in [long,lat] = [WE,SN]

path = mpltPath.Path(polygon)
inside2 = path.contains_points(points)
print(inside2)


# getting the centroids of pixels in each region

centroids = []
pixels = []
for pixel_x in range(4320):
    long = 0.0833*pixel_x - 90 + 0.0833/2
    long_pix = pixel_x
    for pixel_y in range(2160):
        lat = 0.0833*pixel_y - 180 + 0.0833/2
        lat_pix = pixel_y
        
        centroids.append([lat, long])
        pixels.append([lat_pix, long_pix])

polygon = coordinates[0][2][0]
path = mpltPath.Path(polygon)
inside2 = path.contains_points(centroids)
print(inside2)
inside = inside2.tolist()
indices = find_truth(inside)
print(indices)
#centroids[indices]


# Using enumerate to Find Index Positions
def find_truth(list_to_check):
    indices = []
    for idx, value in enumerate(list_to_check):
        if value :
            indices.append(idx)
    return indices

def coord_inside_region(region_idx, region_polygons, points_to_check):
    """
    Find the coordinates of points inside a given region of the world.

    Parameters
    ----------
    region_idx : INT
        Index of the region we want to extract coordinates from.
    region_polygons : LIST
        Coordinates of the contours of the regions.
    points_to_check : LIST
        [lat, long] coordinates in degrees of points to check if inside region or not.

    Returns
    -------
    coord_inside_pix : LIST
        [lat, long] coordinates of points inside the region in pixels.
    coord_inside_deg : TYPE
        [lat, long] coordinates of points inside the region in degrees.

    """
    
    coord_inside_pix = [] #coordinates of points inside the region in pixels
    coord_inside_deg = [] #coordinates of points inside the region in degrees
    
    indices_inside_region = []
    
    subregions = region_polygons[region_idx]
    for subregion in subregions:
        subregion = subregion[0]
        
        polygon = subregion
        path = mpltPath.Path(polygon)
        inside = path.contains_points(points_to_check)
        inside = inside.tolist()
        indices_inside_subregion = find_truth(inside)
        
        for indice in indices_inside_subregion:
            indices_inside_region.append(indice)
            #coord_inside_pix.append(pixels[indice])
            #coord_inside_deg.append(centroids[inside])
    
    return indices_inside_region


coord_inside_region(0, coordinates, centroids)
        