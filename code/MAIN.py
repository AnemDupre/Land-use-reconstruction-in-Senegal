# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:17:08 2024

@author: anem
"""

#%% General initialization

# Set path and rain data to use
path_repository = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated"
country = "Senegal"
NAT_AREA = 19253000 #land area (ha) #country area : 19671000
rain_data2use = "era_wb" #to choose from ["world_bank", "era", "crudata", "era_wb"]

#automatic setup
path_code = path_repository + "\\code"
path_data = path_repository + f"\\data\\{country}\\"
path_results = path_repository + "\\results\\"
seed = 42

#%% Module imports

import os 
os.chdir(path_code)

import inputs_full_fetch
import iterate_with_diff_params
import save
import plot

#%% National scale
numb_samples = 10000
calculation_done = False
header = "2024-06-18_10samples_seed_42" # name with conditions if calculation has been done, format "{yyyy-mm-dd}_{numb_sample}_samples_seed_{seed}", None otherwise

# Calculation
if not(calculation_done):
    inputs_nat = inputs_full_fetch.inputs_full_fetch(path_data, country,
                                                     NAT_AREA, rain_data2use)
    #generate parameter sets
    params_list = iterate_with_diff_params.generate_parameter_sets(numb_samples, seed)
    #simulate land-use evolution
    lu_list = iterate_with_diff_params.iterate_simulation_df(params_list, NAT_AREA, inputs_nat)
    [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
    
    #calculate msd to FAO land-use data
    msd_list = iterate_with_diff_params.iterate_msd_calc(past_df, crop_subs_df, crop_mark_df, fal_df, veg_df, path_data)

    #save
    file_params_msd = save.save_sampling(msd_list, params_list, path_results,
                                         seed)
    file_lu = save.save_outputs(path_results, seed, crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df)

else :
    #fetch sampled parameters, model outputs and msds
    file_params_msds = path_results + header + "_params_msds.xlsx"
    msd_list, params_list = save.load_saved_params_msds(file_params_msds)
    lu_list = save.load_saved_outputs(path_results, header)
    [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list

# Plotting lu and validation
plot.plot_all_lu(lu_list)