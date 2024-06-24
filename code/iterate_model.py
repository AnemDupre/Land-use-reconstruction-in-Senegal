# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:19:07 2024

@author: anem
"""

import iterate_functions
import save

def iterate_model(numb_samples, calculation_done, path_repository, 
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
        save.save_sampling(msd_list, params_list, path_results, seed, modification_marker)
        save.save_outputs(path_results, modification_marker, seed, crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df)

    else :
        #fetch sampled parameters, model outputs and msds

        msd_list, params_list = save.load_saved_params_msds(path_results, header, modification_marker)
        lu_list = save.load_saved_outputs(path_results, header, modification_marker)
        [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list
    
    return msd_list, params_list, lu_list