# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 14:50:09 2024

@author: anem
"""

import json
import matplotlib.path as mpltPath
import input_fetch
import tifffile
import numpy as np
import core

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
            
            regions_names.append(region_name)
            regions_coordinates.append(region_coord)
    return regions_names, regions_coordinates



# getting the centroids of pixels in each region
def all_pixels(pixels_long=4320, pixels_lat=2160,
               degree_per_pixel=0.083333):
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
                     region_polygons):
    
    pixel_centroids_in_regions, pixel_indices_in_regions = [], []
    numb_regions = len(region_polygons)
    
    for region_idx in range(numb_regions):
        pixel_centroids_in_region = []
        pixel_indices_in_region = []
        
        indices_inside_region = coord_inside_region(region_idx, region_polygons, pixel_centroids)
        for indice in indices_inside_region:
            pixel_centroids_in_region.append(pixel_centroids[indice])
            pixel_indices_in_region.append(pixel_indices[indice])
        
        pixel_centroids_in_regions.append(pixel_centroids_in_region)
        pixel_indices_in_regions.append(pixel_indices_in_region)
        
    return pixel_centroids_in_regions, pixel_indices_in_regions



def iterate_species(list_files, pixel_indices_in_regions, regions_names):
    liv_regions = []
    for r in range(len(regions_names)):
        livetock_species = [] #in order: cattle, goats, horse and sheep
        for path in list_files:
            livetock_species.append(get_livestock_regions(path, pixel_indices_in_regions, regions_names))
        liv = input_fetch.calculate_liv(0, livetock_species[0][r], livetock_species[2][r], 
                                        0, livetock_species[1][r], livetock_species[3][r])
        liv_regions.append(liv)
    return liv_regions

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


def all_pixels_pop(pixels_long=743, pixels_lat=526,
               degree_per_pixel=0.008333):
    centroids = []
    indices = []
    
    for pixel_y in range(pixels_lat):
        lat = 16.68333 - (pixel_y+1)*degree_per_pixel/2
        lat_pix = pixel_y
        for pixel_x in range(pixels_long):
            long = -17.51667 + (pixel_x+1)*degree_per_pixel/2
            long_pix = pixel_x
            
            centroids.append([long, lat])
            indices.append([long_pix, lat_pix])
    return centroids, indices



def get_pop_regions(path, pixel_indices_in_regions, regions_names):
    im = tifffile.imread(path)
    #the image is in [lat, long], with lat going from up to down
    imarray = np.array(im) #data in []
    
    pop_regions = []
    for r in range(len(regions_names)):
        pop_region = []
        for coordinates in pixel_indices_in_regions[r]:
            coordinates = [coordinates[1], coordinates[0]]
            pop_region.append(imarray[coordinates[0], coordinates[1]])
        pop_region = core.remove_values_under_thres(pop_region, 0)
        pop_regions.append(sum(pop_region))
    
    #livestock_regions = [sum(livestock_region) for livestock_region in livestock_regions]
    return pop_regions