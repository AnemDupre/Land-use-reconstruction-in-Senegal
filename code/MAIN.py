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
import plot
import modulate_inputs
import sensitivity2inputs
import input_fetch

#%% National level
numb_samples = 1000
rain_data2use = "era_wb" #to choose from ["world_bank", "era", "crudata", "era_wb"]
calculation_done = False
header = None #"2024-06-20_10000samples_seed_42" # name with conditions if calculation has been done, format "{yyyy-mm-dd}_{numb_sample}_samples_seed_{seed}", None otherwise
scale = "national"

inputs_nat = inputs_full_fetch.nat_inputs_full_fetch(path_data, country,
                                                     NAT_AREA, rain_data2use)
params_list, lu_list_nat = iterate_model.iterate_nat(numb_samples, calculation_done, path_repository, NAT_AREA, seed, inputs_nat, header=header, calculate_msd=False)
[crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list_nat

plot.saturation_frequency([lu_list_nat], scale)

# Plotting lu and validation
#plot.plot_all_lu(lu_list, scale, NAT_AREA)
plot.display_median_stack_validation(lu_list_nat, "national", path_results=path_results + "medians_")
plot.plot_reg_lu(lu_list_nat, "national", NAT_AREA, path_results=path_results + "stochastic_individual_")

#%%sensitivity to inputs

changed_inputs = modulate_inputs.change_amplitude(inputs_nat, ["net_imp"], 1.5)
header = "2024-06-25_1000samples_seed_42"

numb_samples = 1000
calculation_done = False
modified_inputs = True
modification_marker = "net_imp_1_5" #"{changed input}_{amplitude}" with a _ instead of commas

msd_list_modified, params_list_modified, lu_list_modified = iterate_model.iterate_nat(numb_samples, calculation_done, path_repository, NAT_AREA, seed, changed_inputs, 
                                                                                      modified_inputs=modified_inputs, modification_marker=modification_marker, header=header)
[crop_df_modified, past_df_modified, crop_subs_df_modified, crop_mark_df_modified, fal_df_modified, un_df_modified, veg_df_modified, intensification_df__modified] = lu_list_modified
plot.plot_all_lu(lu_list_modified)

#%% quantifying sensitivity to inputs

calculation_done = False
numb_samples = 100
mult_factor_list = [0.5, 1.5] #The amplitude of input modification
inputs_list = [["rain"], ["net_imp"], ["pop_rur", "pop_urb"], ["net_imp"], ["yield"], ["liv"]]

rain_data2use = "era_wb"
inputs_nat = inputs_full_fetch.nat_inputs_full_fetch(path_data, country,
                                                     NAT_AREA, rain_data2use)

#calculating for non-modified inputs
params_list, lu_list_original = iterate_model.iterate_nat(numb_samples, calculation_done, path_repository, NAT_AREA, seed, inputs_nat, calculate_msd=False)
#calclating for modified inputs 
lu_modified_dic, divergences_dic = sensitivity2inputs.calculate_modified_outputs(mult_factor_list, inputs_list, inputs_nat,
                                                                                  params_list, NAT_AREA, lu_list_original)


sensitivity2inputs.plot_msd_per_output(divergences_dic)

sensitivity2inputs.plot_msd_all_outputs(divergences_dic)

for key in lu_modified_dic.keys():
    lu_list_modified = lu_modified_dic[key]
    sensitivity2inputs.plot_lu_comparaison(lu_list_original, lu_list_modified, key)

#%%regional scale
import input_fetch, plot

superficies, inputs_reg_dic = inputs_full_fetch.reg_inputs_full_fetch(path_data)
#tappan_data = input_fetch.fetch_other_reg_data("C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\validation_data\\tappan_land_use_data\\reg_lu.xlsx")
header = None
numb_samples = 1000
calculation_done = False

#for region in superficies.keys():
#    inputs_reg_dic[region].drop("biom_prod", axis=1, inplace=True)

for region in superficies.keys():
    inputs_reg = inputs_reg_dic[region]
    params_list, lu_list = iterate_model.iterate_reg(numb_samples, calculation_done, path_repository, superficies[region], seed, inputs_reg[15:], region, header=header)
    
    # Plotting lu and validation
    #plot.plot_all_lu(lu_list, region, superficies[region])
    plot.plot_reg_lu(lu_list, region, superficies[region], path_results=path_results + f"{region}_stochastic_individual_")
    #plot.display_median_stack(lu_list, region)
    plot.display_median_stack_validation(lu_list, region, path_results=path_results  + f"{region}_medians_")


#%% combining the four regions

import fetch_tappan
import inputs_full_fetch

#combining tappan data
scale = "groundnut_bassin"
#combined_tappan_data = fetch_tappan.fetch_tappan('groundnut_bassin', superficies=superficies)
superficy, groundnutbassin_inputs = inputs_full_fetch.combined_reg_full_fetch(path_data)
header = None
numb_samples = 1000
calculation_done = False

#get rid of the biom_prod column
#groundnutbassin_inputs.drop("biom_prod", axis=1, inplace=True)
#groundnutbassin_inputs["yield"] = groundnutbassin_inputs["yield"].apply(lambda x : x*1000)

params_list, lu_list = iterate_model.iterate_reg(numb_samples, calculation_done, 
                                                 path_repository, superficy, seed, 
                                                 groundnutbassin_inputs[15:], scale, header=header)
    
# Plotting lu and validation
#plot.plot_all_lu(lu_list, region, superficies[region])

plot.plot_reg_lu(lu_list, scale, superficy, path_results=path_results + f"{scale}_medians_")
#plot.display_median_stack(lu_list, region)
plot.display_median_stack_validation(lu_list, scale, superficies, path_results=path_results + f"{scale}_stochastic_individual_")


plot.saturation_frequency([lu_list_nat, lu_list], ["national", "groundnut bassin"])
plot.mean_cf([lu_list], ["groundnut bassin"])

#%%
import plot
#plot.mean_cf([lu_list_nat, lu_list], ["national", "groundnut bassin"])
#plot.saturation_frequency([lu_list_nat, lu_list], ["national", "groundnut bassin"])
plot.plot_3_inputs()

#%% groundnut bassin with FAO yield and no biom prod injected
