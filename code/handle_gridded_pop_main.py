# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 14:19:02 2024

@author: anem
"""

import pandas as pd
import handle_gridded_data

path_gridded_pop = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\inputs\\gridded_pop\\"


_ , regions_coord = handle_gridded_data.get_regions_coord()
# [longitude, latitude]


years = ["2000", "2001", "2002",
         "2003", "2004", "2005",
         "2006", "2007", "2008",
         "2009", "2010", "2011",
         "2012", "2013", "2014",
         "2015", "2016", "2017",
         "2018", "2019", "2020"]

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

d = {'year': years}
for year in years :
    
    df = pd.read_csv(path_gridded_pop + f"ppp_SEN_{year}_1km_Aggregated_UNadj.csv")
    # X is longitude and Y latitude
    
    points = []
    for i in range(237052):
        long = df["X"][i]
        lat = df["Y"][i]
        coord =  [long, lat]
        points.append(coord)
    
    indices_regions = []
    inhab_regions = []
    urb_pop_regions = []
    rur_pop_regions = []
    
    for r in range(len(regions_coord)):
        inhab_region = []
        urb_pop_region = []
        rur_pop_region = []
        
        indices_region = handle_gridded_data.coord_inside_region(r, regions_coord, points)
        for indice in indices_region:
            inhab_region.append(df.iloc[indice]["Z"])
            if df.iloc[indice]["Z"] > 250:
                urb_pop_region.append(df.iloc[indice]["Z"])
            else :
                rur_pop_region.append(df.iloc[indice]["Z"])
        
        inhab_region = sum(inhab_region)
        urb_pop_region = sum(urb_pop_region)
        rur_pop_region = sum(rur_pop_region)
        
        inhab_regions.append(inhab_region)
        urb_pop_regions.append(urb_pop_region)
        rur_pop_regions.append(rur_pop_region)
        indices_regions.append(indices_region)
        
        if not("pop_rur_" + regions_names[r] in d):
            d["pop_rur_" + regions_names[r]] = []
            d["pop_urb_" + regions_names[r]] = []
        
        d["pop_rur_" + regions_names[r]].append(rur_pop_region)
        d["pop_urb_" + regions_names[r]].append(urb_pop_region)

# save data

dataframe_pop = pd.DataFrame(data=d)
dataframe_pop.to_excel(path_gridded_pop + "processed_grid.xlsx")

get_pop = pd.read_excel(path_gridded_pop + "processed_grid.xlsx")
