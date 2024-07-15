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

#%% National level
numb_samples = 10
rain_data2use = "era_wb" #to choose from ["world_bank", "era", "crudata", "era_wb"]
calculation_done = False
header = None#"2024-06-20_10000samples_seed_42" # name with conditions if calculation has been done, format "{yyyy-mm-dd}_{numb_sample}_samples_seed_{seed}", None otherwise

inputs_nat = inputs_full_fetch.nat_inputs_full_fetch(path_data, country,
                                                     NAT_AREA, rain_data2use)
msd_list, params_list, lu_list = iterate_model.iterate_nat(numb_samples, calculation_done, path_repository, NAT_AREA, seed, inputs_nat, header=header)
[crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list

# Plotting lu and validation
plot.plot_all_lu(lu_list)

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
import sensitivity2inputs
import matplotlib.pyplot as plt

calculation_done = False
numb_samples = 100
mult_factor = [0.5, 1.5] #The amplitude of input modification
inputs_list = [["rain"], ["net_imp"], ["pop_rur", "pop_urb"], ["net_imp"], ["yield"], ["liv"]]

#non-modified outputs
params_list, lu_list_original = iterate_model.iterate_nat(numb_samples, calculation_done, path_repository, NAT_AREA, seed, inputs_nat, calculate_msd=False)
[crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list

x_labels = ["past", "crop_subs", "crop_mark", 
            "fal", "un", "veg"]
x_locations = [0, 1, 2, 3, 4, 5]

divergences_dic = {}

for k in mult_factor:
    #calculation for modified inputs and divergence estimation
    for input_name in inputs_list:
        fig, ax = plt.subplots()
        changed_inputs = modulate_inputs.change_amplitude(inputs_nat, input_name, k)
        divergences = sensitivity2inputs.calc_divergence(params_list, NAT_AREA, changed_inputs, lu_list_original)
        
        divergences_dic[f"{input_name}_{k}"] = divergences
        # for series, x in zip(divergences, x_locations):
        #     plt.scatter([x]*len(series.to_list()), 
        #                 series.to_list())
        
        # fig.set_dpi(600)
        # ax.set_xticks(x_locations,
        #               x_labels)
        # plt.title(f"{input_name}_at_{mult_factor}")
        # plt.show()
        # plt.close()

for output in x_labels:
    fig, ax = plt.subplots()
    for i, key in enumerate(divergences_dic.keys()):
        plt.scatter([i]*len(divergences_dic[key].index), 
                    divergences_dic[key][output])
    plt.title(output)
    ax.set_xticks(range(len(divergences_dic.keys())),
                  divergences_dic.keys())
    plt.xticks(rotation=90)
    plt.show()
    plt.close()

divergences_sum_output = {}
for i, key in enumerate(divergences_dic.keys()):
    divergences_sum_output[key] = divergences_dic[key].sum(axis=1)
# sorting the dictionary for proper vizualization
divergences_sum_output = dict(sorted(divergences_sum_output.items()))

fig, ax = plt.subplots()
for i, key in enumerate(divergences_sum_output.keys()):
    plt.scatter([i]*len(divergences_sum_output[key].index), 
                divergences_sum_output[key])
    plt.boxplot(divergences_sum_output[key], positions=[i])
plt.title("squared distance all outputs")
ax.set_xticks(range(len(divergences_sum_output.keys())),
              divergences_sum_output.keys())
plt.xticks(rotation=90)
yinf = ax.get_ylim()[0]
ax.set_ylim(yinf, 0.45e16)
plt.show()
plt.close()

#%%regional scale

superficies, inputs_reg = inputs_full_fetch.reg_inputs_full_fetch(path_data)
header = None
numb_samples = 1000
calculation_done = False

for region in superficies.keys():
    params_list, lu_list = iterate_model.iterate_reg(numb_samples, calculation_done, path_repository, superficies[region], seed, inputs_reg, header=header)
    
    # Plotting lu and validation
    plot.plot_all_lu(lu_list)