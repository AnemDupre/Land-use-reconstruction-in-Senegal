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

#%% National scale
numb_samples = 10
calculation_done = True
header = "2024-06-18_10samples_seed_42" # name with conditions if calculation has been done, format "{yyyy-mm-dd}_{numb_sample}_samples_seed_{seed}", None otherwise

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
    file_params_msds = header + "_params_msds"
    msd_list, params_list = save.load_saved_params_msds(file_params_msds)
    lu_list = save.load_saved_outputs(path_results, header)
    [crop_df, past_df, crop_subs_df, crop_mark_df, fal_df, un_df, veg_df, intensification_df] = lu_list


#%% Sampling and calculating
calculation_done = True
date = None #"2024-03-26" #date of calculation if it has been done else none

if calculation_done:
    path2sampling = path_results + '2024-03-26params_random_search_01.xlsx'
    msd_list, params_list = saving_sampling.load_saved_sampling(path2sampling)
    list_lu_values = error_calc.iterate_simulation_return_all_lu_df(params_list[:1000], NAT_AREA, df)
    #contains in order : crop_values, past_values, crop_subs_values, crop_mark_values, fal_values, un_values, veg_values, intensification_values, msd_list
else:
    #fetch
    pass
    path2sampling = path_results + '2024-03-26params_random_search_01.xlsx'
    msd_list, params_list = saving_sampling.load_saved_sampling(path2sampling)



#%% plotting land-use evolution

def plot_lu_multiple_params(list_lu_values, path_results):
    order = ["crop",
             "past",
             "crop_subs",
             "crop_mark",
             "fal",
             "un", 
             "veg"]
    
    ranges = [[0, 1.5*10**7],
              [0, 1.6*10**7],
              [0, 3.2*10**6],
              [0, 2.5*10**6],
              [0, 1.1*10**7],
              [0, 6.5*10**6],
              [0, 1.6*10**7]   
        ]
    
    medianprops = dict(linewidth=3, color='r')#, markeredgecolor='red')
    
    for o, values in enumerate(list_lu_values[:7]):
        save_path = path_results + order[o] + "no_scatter.svg"
        lu_values = values.copy()
        fig, ax = plt.subplots(figsize =(9, 4))
        lu_values.reset_index(inplace=True)
        lu_values.set_index('year', inplace=True)
        lu_values.drop("index", axis=1, inplace=True)
        year = list(set(lu_values.index[:]))
        
        for count, column in enumerate(lu_values.columns[:]):
            
            lu_values.rename({column: f'{count}'})
            #plt.plot(year, lu_values.iloc[:, count])
        

        for i, y in enumerate(year) :
            if i!=0:
                series = lu_values.iloc[i]
                ax.boxplot(series, positions=[y],
                           showfliers=False,
                           #showmeans=True,
                           medianprops=medianprops)
                #ax.scatter([y]*len(series), series)

        if o==0:
            ax.scatter([1975, 2000, 2013], [3260000, 3290000, 4110000], 
                       color="b", label="cropland values from litterature")
        ax.set_ylim(ranges[o])
        
        #changing ticks
        ticks = ax.get_xticks()
        new_ticks = np.delete(ticks, np.where(ticks%2 == 1))
        ax.set_xticks(new_ticks)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{order[o]} (ha)')

        fig.set_dpi(600)
        plt.xticks(rotation=30)
        #♥ax.set_xlim([year[0], year[-1]])
        #fig.savefig(save_path, bbox_inches='tight', format='svg')
        plt.show()

plot_lu_multiple_params(list_lu_values, path_results)