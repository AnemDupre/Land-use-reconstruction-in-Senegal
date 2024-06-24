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
import iterate_model
import save
import plot

#%% National level
numb_samples = 10000
calculation_done = True
header = "2024-06-20_10000samples_seed_42" # name with conditions if calculation has been done, format "{yyyy-mm-dd}_{numb_sample}_samples_seed_{seed}", None otherwise

inputs_nat = inputs_full_fetch.inputs_full_fetch(path_data, country,
                                                 NAT_AREA, rain_data2use)
msd_list, params_list, lu_list = iterate_model.iterate_model(numb_samples, calculation_done, path_repository, NAT_AREA, seed, inputs_nat, header=header)
[crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list

# Plotting lu and validation
plot.plot_all_lu(lu_list)

#%%sensitivity to inputs
import modulate_inputs
import iterate_model

changed_inputs = modulate_inputs.change_amplitude(inputs_nat, ["liv"], 0.5)

numb_samples = 1000
calculation_done = False
modified_inputs = True
modification_marker = "liv_0_5" #"{changed input}_{amplitude}" with a _ instead of commas

msd_list_rain0_5, params_list_rain0_5, lu_list_rain0_5 = iterate_model.iterate_model(numb_samples, calculation_done, path_repository, NAT_AREA, seed, changed_inputs, modified_inputs=modified_inputs, modification_marker=modification_marker)
[crop_df_rain0_5, past_df_rain0_5, crop_subs_df_rain0_5, crop_mark_df_rain0_5, fal_df_rain0_5, un_df_rain0_5, veg_df_rain0_5, intensification_df_rain0_5] = lu_list_rain0_5
plot.plot_all_lu(lu_list_rain0_5)
#%%regional scale