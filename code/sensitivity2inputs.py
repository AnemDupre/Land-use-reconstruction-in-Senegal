# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 11:40:04 2024

@author: anem
"""

import iterate_functions



def calc_divergence(params_list, NAT_AREA, 
                    inputs_modified, lu_list_original):
    lu_list_modified = iterate_functions.iterate_simulation_df(params_list, NAT_AREA, inputs_modified)
    [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list_modified
    div_list = []

    for output_modified, output_original in zip(lu_list_modified[:-1], lu_list_original[:-1]):
        divergence = output_original.subtract(output_modified)
        divergence = divergence.apply(lambda x: x ** 2)
        divergence = divergence.sum(axis=1)
        #divergence = divergence.sum()
        div_list.append(divergence)
    
    return div_list
    


def calc_dist(df1, df2, items=["past", "crop_subs", "crop_mark", "fal", "un", "veg"]):
    tot_dif = 0
    for item in items :
        dif = abs(df1[item] - df2[item])
        dif = dif.sum()
        tot_dif += dif
    return tot_dif 