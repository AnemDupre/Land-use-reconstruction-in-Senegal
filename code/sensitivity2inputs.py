# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 11:40:04 2024

@author: anem
"""

import iterate_functions
import pandas as pd
import modulate_inputs
import matplotlib.pyplot as plt
import numpy as np



def calc_divergence(params_list, NAT_AREA, 
                    inputs_modified, lu_list_original):
    
    lu_list_modified = iterate_functions.iterate_simulation_df(params_list, NAT_AREA, inputs_modified)
    output_names = ["past", "crop_subs", "crop_mark", 
                    "fal", "un", "veg"]
    div_list = {}

    for output_name, output_modified, output_original in zip(output_names, lu_list_modified[1:-1], lu_list_original[1:-1]):
        divergence = output_original.subtract(output_modified)
        divergence = divergence.apply(lambda x: x ** 2)
        divergence = divergence.sum(axis=0)
        divergence = divergence.apply(lambda x: x/len(params_list))
        divergence = divergence.to_list()

        div_list[output_name] = divergence
    
    div_list = pd.DataFrame(div_list)
    return lu_list_modified, div_list



def calculate_modified_outputs(mult_factor_list, inputs_list, inputs_nat,
                               params_list, NAT_AREA, lu_list_original):

    divergences_dic = {}
    lu_modified_dic = {}
    
    for mult_factor in mult_factor_list:
        #calculation for modified inputs and divergence estimation
        for input_name in inputs_list:
            changed_inputs = modulate_inputs.change_amplitude(inputs_nat, input_name, mult_factor)
            lu_list_modified, divergences = calc_divergence(params_list, NAT_AREA, changed_inputs, lu_list_original)
            
            divergences_dic[f"{input_name}_{mult_factor}"] = divergences
            lu_modified_dic[f"{input_name}_{mult_factor}"] = lu_list_modified
    # sorting the dictionary for proper vizualization
    divergences_dic = dict(sorted(divergences_dic.items()))
        
    return lu_modified_dic, divergences_dic



def plot_msd_per_output(divergences_dic):
    x_labels = ["past", "crop_subs", "crop_mark", 
                    "fal", "un", "veg"]
    #x_locations = [i for i in range(len(x_labels))]
    
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



def plot_msd_all_outputs(divergences_dic):
    divergences_sum_output = {}
    for i, key in enumerate(divergences_dic.keys()):
        divergences_sum_output[key] = divergences_dic[key].sum(axis=1)

    fig, ax = plt.subplots()
    for i, key in enumerate(divergences_sum_output.keys()):
        plt.scatter([i]*len(divergences_sum_output[key].index), 
                    divergences_sum_output[key])
        plt.boxplot(divergences_sum_output[key], positions=[i])
    plt.title("squared distance all outputs")
    ax.set_xticks(range(len(divergences_sum_output.keys())),
                  divergences_sum_output.keys())
    plt.xticks(rotation=90)
    #yinf = ax.get_ylim()[0]
    ax.set_ylim(-0.5e13, 0.45e14)
    plt.show()
    plt.close()



def plot_lu_comparaison(lu_list_original, lu_list_modified, key, path_results=None):
    
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    
    ranges = [[0, 1.5*10**7],
              [0, 1.6*10**7],
              [0, 3.2*10**6],
              [0, 2.5*10**6],
              [0, 1.1*10**7],
              [0, 6.5*10**6],
              [0, 1.6*10**7]   
        ]
    
    medianprops = dict(linewidth=3, color='r')#, markeredgecolor='red')

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(2*9,3*8))
    for c, (values_original, values_modified) in enumerate(zip(lu_list_original[1:7], lu_list_modified[1:7])):
        if c<3:
            ax = axes[c][0]
        else:
            ax = axes[c-3][1]
        
        #formatting our dataframes
        lu_original = values_original.copy()
        lu_original.reset_index(inplace=True)
        lu_original.set_index('year', inplace=True)
        lu_original.drop("index", axis=1, inplace=True)
        
        lu_modified = values_modified.copy()
        lu_modified.reset_index(inplace=True)
        lu_modified.set_index('year', inplace=True)
        lu_modified.drop("index", axis=1, inplace=True)
        
        year = list(set(lu_original.index[:]))
        
        for count, column in enumerate(lu_original.columns[:]):
            
            lu_original.rename({column: f'{count}'})
            lu_modified.rename({column: f'{count}'})
            #plt.plot(year, lu_original.iloc[:, count])
        
        
        for i, y in enumerate(year) :
            if i!=0:
                series_or = lu_original.iloc[i]
                ax.boxplot(series_or, positions=[y],
                           showfliers=False,
                           #showmeans=True,
                           medianprops=medianprops)
                
                series_mod = lu_modified.iloc[i]
                ax.boxplot(series_mod, positions=[y+0.5],
                           showfliers=False,
                           patch_artist=True,
                           boxprops=dict(facecolor="blue", color="blue"),
                           #showmeans=True,
                           medianprops=medianprops)
                #ax.scatter([y]*len(series), series)

        #if c==0:
            #ax.scatter([1975, 2000, 2013], [3260000, 3290000, 4110000], 
                       #color="b", label="cropland values from litterature")
        #ax.set_ylim(ranges[c])
        
        #changing ticks
        ticks = ax.get_xticks()
        new_ticks = np.delete(ticks, np.where(ticks%2 == 1))
        new_ticks = np.delete(new_ticks, np.where(new_ticks%1 != 0))
        ax.set_xticks(new_ticks, new_ticks, rotation=30)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{categories[c]} (ha)')

        #plt.xticks(rotation=30)
        if path_results!=None:
            save_path = path_results + categories[c] + "no_scatter.svg"
            fig.savefig(save_path, bbox_inches='tight', format='svg')
        #♥ax.set_xlim([year[0], year[-1]])
    
    fig.set_dpi(600)
    plt.title(key)
    plt.show()
