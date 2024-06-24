# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:50:09 2024

@author: anem
"""

import json
import matplotlib.path as mpltPath

path = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\geography\\"
file = path + "gadm41_SEN_1.json"
# data from https://gadm.org/index.html

def get_regions_coord(file=file):
    regions_names = []
    regions_coordinates = []
    
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
            regions_coordinates.append(region_coord)
    return regions_names, regions_coordinates



# getting the centroids of pixels in each region
def all_pixels(pixels_long=4320, pixels_lat=2160,
               degree_per_pixel=0.0833):
    centroids = []
    indices = []
    for pixel_x in range(pixels_long):
        long = degree_per_pixel*pixel_x - 90 + degree_per_pixel/2
        long_pix = pixel_x
        for pixel_y in range(pixels_lat):
            lat = degree_per_pixel*pixel_y - 180 + degree_per_pixel/2
            lat_pix = pixel_y
            
            centroids.append([lat, long])
            indices.append([lat_pix, long_pix])
    return centroids, indices



# Using enumerate to find index positions
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

    return indices_inside_region



def coord_all_region(pixel_centroids, pixel_indices, 
                     region_polygons, points_to_check):
    
    pixel_centroids_in_regions, pixel_indices_in_regions = [], []
    numb_regions = len(region_polygons)
    for region_idx in range(numb_regions):
        pixel_centroids_in_region = []
        pixel_indices_in_region = []
        
        indices_inside_region = coord_inside_region(region_idx, region_polygons, points_to_check)
        for indice in indices_inside_region:
            pixel_centroids_in_region.append(pixel_centroids[indice])
            pixel_indices_in_region.append(pixel_indices[indice])
        
        pixel_centroids_in_regions.append(pixel_centroids_in_region)
        pixel_indices_in_regions.append(pixel_indices_in_region)
        
    return pixel_centroids_in_regions, pixel_indices_in_regions




