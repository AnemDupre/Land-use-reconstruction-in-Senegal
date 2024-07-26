# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:26:22 2024

@author: anem
"""

import pandas as pd
from functools import reduce
import input_fetch



def fetch_tappan(scale, superficies=None):
    #validation data
    path_tappan = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\validation_data\\tappan_land_use_data\\"
    
    if scale=="national":
        path_tappan+="nat_lu.xlsx"
        val_data = pd.read_excel(path_tappan)
    elif scale in ["Diourbel", "Fatick", "Kaffrine_Kaolack", "Thies"]:
        path_tappan+="reg_lu.xlsx"
        xls = pd.ExcelFile(path_tappan)
        val_data = pd.read_excel(xls, scale)
    elif scale == "groundnut_bassin":
        path_tappan+="reg_lu.xlsx"
        xls = pd.ExcelFile(path_tappan)
        temp_data = input_fetch.fetch_other_reg_data(path_tappan)
        
        val_data = combine_tappan(temp_data, superficies)
        
    return val_data



def combine_tappan(tappan_data, superficies):
    copy_tappan = tappan_data.copy()
    
    for region in superficies.keys(): #iterating over regions
        df = copy_tappan[region]
        superficy = superficies[region]
        df['crop_prop'] = df['crop_prop'].map(lambda x : x * superficy)
        df['veg_past_prop'] = df['veg_past_prop'].map(lambda x : x * superficy)
        
    combined = reduce(lambda a, b: a.add(b, fill_value=0), 
                      [copy_tappan[region] for region in superficies.keys()])
    
    full_superficy = sum(superficies.values())
    combined = combined.div(full_superficy)
    combined["year"] = copy_tappan["Diourbel"]["year"]
    
    return combined
