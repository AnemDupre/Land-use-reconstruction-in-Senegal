# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:17:08 2024

@author: anem
"""

#%% General initialization

# Set paths
path_repository = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\land_use_repository_v3"
path_code = path_repository + "\\code"
path_data = path_repository + "\\data\\"
path_results = path_repository + "\\results\\"
seed = 42

#%% Module imports

import os 
os.chdir(path_code)
import iterate_model
import plot
import fetch

#%% National level

#settings
numb_samples = 10
scale = "senegal"
NAT_AREA = 19253000
path_inputs = path_data + f"\\inputs\\{scale}_inputs.xlsx"
path_validation = path_data + f"\\validation_data\\{scale}_lu.xlsx"

#fetch inputs
inputs_nat = fetch.df(path_inputs)

#generate parameter samples and calculate model outputs
params_list, lu_list_nat = iterate_model.iterate(numb_samples, NAT_AREA, 
                                                 seed, inputs_nat)
[crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df, biom_prod_df, sum_lu_df] = lu_list_nat

#plotting results
plot.saturation_frequency([lu_list_nat], [scale])
plot.display_median_stack_validation(lu_list_nat, scale, path_validation, NAT_AREA, path_results=path_results + "medians_")
plot.plot_reg_lu(lu_list_nat, scale, NAT_AREA, path_results=path_results + "stochastic_individual_")

#%% Groundnut basin scale

#settings
numb_samples = 10
scale = "groundnut"
GROUNDNUT_AREA = 3496200
path_inputs = path_data + f"\\inputs\\{scale}_inputs.xlsx"
path_validation = path_data + f"\\validation_data\\{scale}_lu.xlsx"

#fetch inputs
inputs_reg = fetch.df(path_inputs)
inputs_reg["yield"] = inputs_reg["yield"].apply(lambda x: x*2)

#get rid of the biom_prod column
#groundnutbassin_inputs.drop("biom_prod", axis=1, inplace=True)

params_list, lu_list_reg = iterate_model.iterate(numb_samples, GROUNDNUT_AREA, 
                                                 seed, inputs_reg, preservation=False, 
                                                 calculate_demand=True)

# Plotting lu and validation
#plot.plot_all_lu(lu_list, region, superficies[region])

plot.plot_reg_lu(lu_list_reg, scale, GROUNDNUT_AREA, path_results=path_results + f"{scale}_medians_")

#plot.display_median_stack(lu_list, region)
plot.display_median_stack_validation(lu_list_reg, scale, path_validation, GROUNDNUT_AREA, path_results=path_results + f"{scale}_stochastic_individual_")


plot.saturation_frequency([lu_list_nat, lu_list_reg], ["national", "groundnut bassin"])
plot.mean_cf([lu_list_reg], ["groundnut bassin"])


#%% plotting the inputs for both scales

plot.plot_3_inputs_per_ha(inputs_nat, inputs_reg, NAT_AREA, 
                          GROUNDNUT_AREA, lu_list_nat, lu_list_reg)
