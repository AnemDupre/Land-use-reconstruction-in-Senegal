# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:36:56 2024

@author: anem
"""

import numpy as np
import merge
import model
import fetch_fao_land_use



def generate_parameter_sets(numb, seed):
    np.random.seed(seed)
    
    #define ranges 
    biom_conso_min_range = [1.7, 3.0]
    biom_conso_max_range = [3.4, 6.1]
    food_conso_range = [109.8, 327.1]
    cf_range = [1, 3]
    fuel_conso_rur_range = [0.41, 1.26]
    fuel_conso_urb_range = [0.41, 1.26]
    veg_prod_range = [0.1, 3.0]
    a_biom_prod_range = [0.0025, 0.005]
    b_biom_prod_range = [-0.20, 0.30]
    crop_past_ratio_range = [1/5, 2/3]
    cf_inf_range = [0, 0.5]
    
    params_list_rand = []
    for i in range(numb):
        params = {"biom_conso_min":np.random.uniform(low=biom_conso_min_range[0],
                                                     high=biom_conso_min_range[1]),
                  "biom_conso_max":np.random.uniform(low=biom_conso_max_range[0],
                                                     high=biom_conso_max_range[1]),
                  "food_conso":np.random.uniform(low=food_conso_range[0],
                                                 high=food_conso_range[1]),
                  "cf":np.random.uniform(low=cf_range[0],
                                         high=cf_range[1]),
                  "fuel_conso_rur":np.random.uniform(low=fuel_conso_rur_range[0],
                                                     high=fuel_conso_rur_range[1]),
                  "fuel_conso_urb":np.random.uniform(low=fuel_conso_urb_range[0],
                                                     high=fuel_conso_urb_range[1]),
                  "veg_prod":np.random.uniform(low=veg_prod_range[0],
                                               high=veg_prod_range[1]),
                  "a_biom_prod":np.random.uniform(low=a_biom_prod_range[0],
                                                  high=a_biom_prod_range[1]),
                  "b_biom_prod":np.random.uniform(low=b_biom_prod_range[0],
                                                     high=b_biom_prod_range[1]),
                  "crop_past_ratio":np.random.uniform(low=crop_past_ratio_range[0],
                                                     high=crop_past_ratio_range[1]),
                  "cf_inf":np.random.uniform(low=cf_inf_range[0],
                                             high=cf_inf_range[1])
                  }
        params_list_rand.append(params)
        
    return params_list_rand #list of num parameter sets randomely sampled



def iterate_simulation_df(params_list, NAT_AREA, inputs):
    crop_dfs = []
    past_dfs = []
    crop_subs_dfs = []
    crop_mark_dfs = []
    fal_dfs = []
    un_dfs = []
    veg_dfs = []
    intensification_dfs = []
    
    # Iterate over each point in the cluster
    for point in params_list:
        land_use_model = model.LandUseModel(NAT_AREA, inputs, params=point)
        land_use_model.iterate()
        crop_df = land_use_model.lu_memory[["year", "crop"]].rename(columns={'crop': 'crop'})
        past_df = land_use_model.lu_memory[["year", "past"]]
        crop_subs_df = land_use_model.lu_memory[["year", "crop_subs"]]
        crop_mark_df = land_use_model.lu_memory[["year", "crop_mark"]]
        fal_df = land_use_model.lu_memory[["year", "fal"]]
        un_df = land_use_model.lu_memory[["year", "un"]]
        veg_df = land_use_model.lu_memory[["year", "veg"]]
        intensification_df = land_use_model.lu_memory[["year", "intensification"]]
        
        #adding the results to the corresponding lists
        crop_dfs.append(crop_df)
        past_dfs.append(past_df)
        crop_subs_dfs.append(crop_subs_df)
        crop_mark_dfs.append(crop_mark_df)
        fal_dfs.append(fal_df)
        un_dfs.append(un_df)
        veg_dfs.append(veg_df)
        intensification_dfs.append(intensification_df)
        
    # Append the final DataFrame to the list
    crop_values = merge.merge_df(crop_dfs, column="year")  
    past_values = merge.merge_df(past_dfs, column="year")  
    crop_subs_values = merge.merge_df(crop_subs_dfs, column="year")  
    crop_mark_values = merge.merge_df(crop_mark_dfs, column="year")  
    fal_values = merge.merge_df(fal_dfs, column="year")  
    un_values = merge.merge_df(un_dfs, column="year")  
    veg_values = merge.merge_df(veg_dfs, column="year")  
    intensification_values = merge.merge_df(intensification_dfs, column="year")  
    
    land_use_list = [crop_values, past_values, crop_subs_values, crop_mark_values, fal_values, un_values, veg_values, intensification_values]
    
    return land_use_list



def iterate_msd_calc(past_df, crop_subs_df, 
                     crop_mark_df, fal_df, 
                     veg_df, path_data):
    
    numb_sim = len(past_df.columns)
    
    #fetching fao land use data
    fao_crop = fetch_fao_land_use.fetch_temp_and_perm_crop(path_data + "fao_land_use_data\\temporary_and_permanent_crop.xlsx")
    fao_fal = fetch_fao_land_use.fetch_fal(path_data + "fao_land_use_data\\temporary_fallows.xlsx")
    fao_past = fetch_fao_land_use.fetch_past(path_data + "fao_land_use_data\\meadows_and_pasture.xlsx")
    fao_veg = fetch_fao_land_use.fetch_veg(path_data + "fao_land_use_data\\forest_land.xlsx")
    
    msd_list = []

    for sim in range(numb_sim-1):
        #compare with our results
        model_past = past_df.iloc[:,[0, sim+1]].copy()
        past_compare_df = merge.merge_df([model_past, fao_past], column="year")
        past_compare_df["msd_past"] = (past_compare_df.iloc[:, 1] - past_compare_df["past_fao"])**2
        past_msd = past_compare_df["msd_past"].sum()/len(past_compare_df.index)
        
        model_crop_subs = crop_subs_df.iloc[:,[0, sim+1]].copy()
        model_crop_mark = crop_mark_df.iloc[:,[0, sim+1]].copy()
        model_crop = merge.merge_df([model_crop_subs, model_crop_mark], column="year")
        model_crop["crop_subs_mark"] = model_crop.iloc[:,1] + model_crop.iloc[2]
        crop_df = merge.merge_df([model_crop, fao_crop], column="year")
        crop_df["msd_crop"] = (crop_df["crop_subs_mark"] - crop_df["crop_fao"])**2
        crop_msd = crop_df["msd_crop"].sum()/len(crop_df.index)
        
        model_fal = fal_df.iloc[:,[0, sim+1]].copy()
        fal_compare_df = merge.merge_df([model_fal, fao_fal], column="year")
        fal_compare_df["msd_fal"] = (fal_compare_df.iloc[:,1] - fal_compare_df["fal_fao"])**2
        fal_msd = fal_compare_df["msd_fal"].sum()/len(fal_compare_df.index)
           
        model_veg = veg_df.iloc[:,[0, sim+1]].copy()
        veg_compare_df = merge.merge_df([model_veg, fao_veg], column="year")
        veg_compare_df["msd_veg"] = (veg_compare_df.iloc[:,1] - veg_compare_df["veg_fao"])**2
        veg_msd = veg_compare_df["msd_veg"].sum()/len(veg_compare_df.index)    
        
        msd = (past_msd + crop_msd + fal_msd + veg_msd)/4
        msd_list.append(msd)
    return msd_list