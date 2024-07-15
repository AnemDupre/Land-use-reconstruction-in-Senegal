# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:19:07 2024

@author: anem
"""

import iterate_functions
import save

def iterate_nat(numb_samples, calculation_done, path_repository, 
                NAT_AREA, seed, inputs, 
                modified_inputs=False, modification_marker=None,
                header=None, country="Senegal"):
    #setting path
    if modified_inputs:
        path_results = path_repository + "\\results\\national\\modified_inputs\\"
    else:
        path_results = path_repository + "\\results\\national\\original_inputs\\"
        
    path_data = path_repository + f"\\data\\{country}\\"
    
    if not(calculation_done):
        #generate parameter sets
        params_list = iterate_functions.generate_parameter_sets(numb_samples, seed)
        #simulate land-use evolution
        lu_list = iterate_functions.iterate_simulation_df(params_list, NAT_AREA, inputs)
        [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
        
        #calculate msd to FAO land-use data
        msd_list = iterate_functions.iterate_msd_calc(past_df, crop_subs_df, crop_mark_df, fal_df, veg_df, path_data)

        #save
        save.save_sampling(params_list, path_results, seed, modification_marker, msd_list=msd_list)
        save.save_outputs(path_results, seed, 
                          crop_df, past_df, crop_subs_df, crop_mark_df, 
                          fal_df, un_df, veg_df, intensification_df,
                          modification_marker=modification_marker)

    else :
        #fetch sampled parameters, model outputs and msds

        msd_list, params_list = save.load_saved_params_msds(path_results, header, modification_marker=modification_marker)
        lu_list = save.load_saved_outputs(path_results, header, modification_marker=modification_marker)
        [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
    
    return msd_list, params_list, lu_list



def iterate_reg(numb_samples, calculation_done, path_repository, 
                surface, seed, inputs,
                header=None, country="Senegal"):
    
    path_results = path_repository + "\\results\\regional\\"
    
    if not(calculation_done):
        #generate parameter sets
        params_list = iterate_functions.generate_parameter_sets(numb_samples, seed)
        #simulate land-use evolution
        lu_list = iterate_functions.iterate_simulation_df(params_list, surface, inputs)
        [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
        
        #save
        save.save_sampling(params_list, path_results, seed)
        save.save_outputs(path_results, seed, 
                          crop_df, past_df, crop_subs_df, crop_mark_df, 
                          fal_df, un_df, veg_df, intensification_df)

    else :
        #fetch sampled parameters, model outputs and msds

        params_list = save.load_saved_params_msds(path_results, header)
        lu_list = save.load_saved_outputs(path_results, header)
        [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
    
    return params_list, lu_list
    
    
    