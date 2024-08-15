# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 20:20:04 2024

@author: anem
"""

import pandas as pd



def df(path):
    inputs_df = pd.read_excel(path)
    return inputs_df



def parameter_ranges():
    return {"biom_conso_min" : [1.7, 3.0],
            "biom_conso_max" : [3.4, 6.1],
            "food_conso" : [109.8, 327.1],
            "cf" : [1, 3],
            "fuel_conso_rur" : [0.41, 1.26],
            "fuel_conso_urb" : [0.41, 1.26],
            "veg_prod" : [0.1, 3.0],
            "a_biom_prod" : [0.0025, 0.005],
            "b_biom_prod" : [-0.20, 0.30],
            "crop_past_ratio" : [0, 1]}