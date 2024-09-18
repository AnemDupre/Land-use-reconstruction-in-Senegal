# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:17:08 2024

@author: anem
"""

#%% Module imports and general initialization

#set paths
PATH_REPOSITORY = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\land_use_repository_v3"
PATH_CODE = PATH_REPOSITORY + "\\code"
PATH_DATA = PATH_REPOSITORY + "\\data\\"
PATH_RESULTS = PATH_REPOSITORY + "\\results\\"
#set seeds
SEED = 42
#imports
import os
os.chdir(PATH_CODE)
import iterate_model
import plot
import fetch
import sensitivity

#%% National level

#settings
NUMB_SAMPLES_NAT = 1000
SCALE = "senegal"
NAT_AREA = 19253000
path_inputs = PATH_DATA + f"\\inputs\\{SCALE}_inputs.xlsx"
path_validation = PATH_DATA + f"\\validation_data\\{SCALE}_lu.xlsx"

#fetch inputs
inputs_nat = fetch.df(path_inputs)
#generate parameter samples and calculate model outputs
params_list, lu_list_nat = iterate_model.iterate(NUMB_SAMPLES_NAT, NAT_AREA,
                                                 SEED, inputs_nat)

# Plotting
#results
plot.land_uses_boxplots(lu_list_nat, SCALE, NAT_AREA,
                        path_results=PATH_RESULTS+f"{NUMB_SAMPLES_NAT}")
plot.median_stack_and_validation(lu_list_nat, SCALE,
                               path_validation, NAT_AREA,
                               path_results=PATH_RESULTS+f"{NUMB_SAMPLES_NAT}")
#intensification proxys
plot.intensification_proxys(lu_list_nat, inputs_nat,
                            params_list,
                            path_results=PATH_RESULTS+f"{NUMB_SAMPLES_NAT}")

#%% Sensitivity analysis on parameter values

#calculating Sobol first order indices and delta indices
sensitivity = sensitivity.test_param_sensitivity(NAT_AREA, inputs_nat, 10000)
#plotting
plot.sensitivity_heatmap(sensitivity, path_results=PATH_RESULTS)

#%% Groundnut basin SCALE

#settings
NUMB_SAMPLES_REG = 1000
SCALE = "groundnut"
GROUNDNUT_AREA = 3496200
path_inputs = PATH_DATA + f"\\inputs\\{SCALE}_inputs.xlsx"
path_validation = PATH_DATA + f"\\validation_data\\{SCALE}_lu.xlsx"

#fetch inputs
inputs_reg = fetch.df(path_inputs)
inputs_reg["yield"] = inputs_reg["yield"].apply(lambda x: x*2)

#get rid of the biom_prod column
#groundnutbassin_inputs.drop("biom_prod", axis=1, inplace=True)

params_list, lu_list_reg = iterate_model.iterate(NUMB_SAMPLES_REG, GROUNDNUT_AREA,
                                                 SEED, inputs_reg,
                                                 calculate_demand=True)

# Plotting results
plot.land_uses_boxplots(lu_list_reg, SCALE, GROUNDNUT_AREA,
                        path_results=PATH_RESULTS +\
                            f"{NUMB_SAMPLES_REG}_{SCALE}")
plot.median_stack_and_validation(lu_list_reg, SCALE,
                               path_validation, GROUNDNUT_AREA,
                               path_results=PATH_RESULTS +\
                                   f"{NUMB_SAMPLES_REG}_{SCALE}")

#%% plotting the inputs for both scales

plot.all_inputs([inputs_nat, inputs_reg],
                [NAT_AREA, GROUNDNUT_AREA],
                [lu_list_nat, lu_list_reg],
                path_results=PATH_RESULTS)

plot.rain([inputs_nat, inputs_reg],
          path_results=PATH_RESULTS)
