# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 11:40:04 2024

@author: anem
"""

import iterate_functions
import pandas as pd


def calc_divergence(params_list, NAT_AREA, 
                    inputs_modified, lu_list_original):
    lu_list_modified = iterate_functions.iterate_simulation_df(params_list, NAT_AREA, inputs_modified)
    output_names = ["past", "crop_subs", "crop_mark", 
                    "fal", "un", "veg"]
    div_list = {}

    for output_name, output_modified, output_original in zip(output_names, lu_list_modified[1:-1], lu_list_original[1:-1]):
        divergence = output_original.subtract(output_modified)
        divergence = divergence.apply(lambda x: x ** 2)
        divergence = divergence.sum(axis=0).to_list()
        print(divergence)


        div_list[output_name] = divergence
    div_list = pd.DataFrame(div_list)
    return div_list
    


def calc_dist(df1, df2, items=["past", "crop_subs", "crop_mark", "fal", "un", "veg"]):
    tot_dif = 0
    for item in items :
        dif = abs(df1[item] - df2[item])
        dif = dif.sum()
        tot_dif += dif
    return tot_dif 