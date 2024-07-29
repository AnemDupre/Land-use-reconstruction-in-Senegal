# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:17:24 2024

@author: anem
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import fetch_tappan



def plot_all_lu(list_lu_values, scale, superficy, path_results=None):
    categories = ["crop", "past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    
    val_data = fetch_tappan.fetch_tappan(scale)
    
    # ranges = [[0, 1.5*10**7],
    #           [0, 1.6*10**7],
    #           [0, 3.2*10**6],
    #           [0, 2.5*10**6],
    #           [0, 1.1*10**7],
    #           [0, 6.5*10**6],
    #           [0, 1.6*10**7]   
    #     ]
    
    medianprops = dict(linewidth=3, color='r')#, markeredgecolor='red')
    
    for c, values in enumerate(list_lu_values[:7]):
        lu_values = values.copy()
        fig, ax = plt.subplots(figsize =(9, 4))
        lu_values.reset_index(inplace=True)
        lu_values.set_index('year', inplace=True)
        lu_values.drop("index", axis=1, inplace=True)
        year = list(set(lu_values.index[:]))
        
        lu_values = lu_values.div(superficy)
        
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

        if c==0:
            ax.scatter(val_data["year"], val_data["crop_prop"], 
                       color="b", label="Cropland values from litterature")
        elif c==6:
            ax.scatter(val_data["year"], val_data["veg_prop"], 
                       color="b", label="Vegetated areas from litterature")    
        
        #ax.set_ylim(ranges[c])
        
        #changing ticks
        ticks = ax.get_xticks()
        new_ticks = np.delete(ticks, np.where(ticks%2 == 1))
        ax.set_xticks(new_ticks)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{categories[c]} (ha)')

        fig.set_dpi(600)
        plt.xticks(rotation=30)
        if path_results!=None:
            save_path = path_results + categories[c] + "no_scatter.svg"
            fig.savefig(save_path, bbox_inches='tight', format='svg')
        #♥ax.set_xlim([year[0], year[-1]])
        plt.show()



def plot_reg_lu(lu_list, region, region_surface, path_results=None):
    
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
        
    medianprops = dict(linewidth=3, color='r')#, markeredgecolor='red')

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12,15))
    #plt.title(region)
    for c, values in enumerate(lu_list[1:7]):
        if c<3:
            ax = axes[c][0]
        else:
            ax = axes[c-3][1]
        
        #formatting our dataframes
        lu_original = values.copy()
        lu_original.reset_index(inplace=True)
        lu_original.set_index('year', inplace=True)
        lu_original.drop("index", axis=1, inplace=True)
        
        lu_original = lu_original.div(region_surface)
        
        year = list(set(lu_original.index[:]))
        
        for count, column in enumerate(lu_original.columns[:]):
            
            lu_original.rename({column: f'{count}'})
            #plt.plot(year, lu_original.iloc[:, count])
        
        
        for i, y in enumerate(year) :
            if i!=0:
                series_or = lu_original.iloc[i]
                ax.boxplot(series_or, positions=[y],
                           showfliers=False,
                           #showmeans=True,
                           medianprops=medianprops)
        
        #changing ticks
        ticks = ax.get_xticks()
        new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
        #new_ticks = np.delete(new_ticks, np.where(new_ticks%1 != 0))
        ax.set_xticks(new_ticks, new_ticks, rotation=30)
        
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{categories[c]} (ha)')

        #plt.xticks(rotation=30)
    if path_results!=None:
        save_path = path_results + categories[c] + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')
    
    fig.set_dpi(600)
    
    plt.show()



def display_median_stack(lu_list, region, path_results=None):#, items=["un","crop", "past", "veg"]):
    
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    
    plt.style.use('seaborn-v0_8-colorblind')

    # Calculating normalized medians
    year = list(set(lu_list[0]["year"]))
    
    sum_medians = pd.DataFrame(columns=["median_sum"])
    sum_medians["year"] = lu_list[0]["year"]
    
    medians_dataframe = pd.DataFrame(columns={"year": lu_list[0]["year"]})
    for e, output in enumerate(lu_list[1:7]):
        kept_columns = output.columns[1:]
        medians = output[kept_columns].median(axis=1)
        medians_dataframe[categories[e]] = medians

    sum_medians = medians_dataframe[list(medians_dataframe.columns[1:])].sum(axis=1)
    #sum validated
    medians_dataframe = medians_dataframe.div(sum_medians, axis=0)

    land_uses = []
    for e in range(len(lu_list[1:7])):
        land_uses.append((categories[e], medians_dataframe[categories[e]].tolist()))
    
    land_uses = dict(land_uses)
    #return land_uses
    fig, ax = plt.subplots(figsize =(5, 2))

    #ax.axhline(y=NAT_AREA, color="black", linestyle=":", label="national area")
    ax.stackplot(year, land_uses.values(),
                 labels=land_uses.keys(), alpha=0.8)
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    ax.set_title('Evolution of land use')
    ax.set_xlabel('Year')
    ax.set_ylabel('Area (ha)')
    plt.title(region)
    fig.set_dpi(600) 
    ax.set_xlim([year[0], year[-1]])
    if path_results!=None:
        savepath = path_results + "land_use_evolution" + ".svg"
        fig.savefig(savepath, bbox_inches='tight', format='svg')
    plt.show()



def display_median_stack_validation(lu_list, scale, superficies=None, path_results=None):
    """
    Plots the medians of land use outputs for categories
    "past", "crop_subs", "crop_mark", "fal", "un", "veg".
    Tappan data points can be added for validation.

    Parameters
    ----------
    lu_list : TUPLE OF DATAFRAMES
        With dataframes corresponding to each output
        category from the model.
    scale : STR
        Either "national" or the name of 
        the considered region.
    path_results : STR, optional
        Where to save the figure.
        The default is None.

    Returns
    -------
    None.

    """
    #validation data
    val_data = fetch_tappan.fetch_tappan(scale, superficies=superficies)
    
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    
    plt.style.use('seaborn-v0_8-colorblind')

    # Calculating normalized medians
    year = list(set(lu_list[0]["year"]))
    
    sum_medians = pd.DataFrame(columns=["median_sum"])
    sum_medians["year"] = lu_list[0]["year"]
    
    medians_dataframe = pd.DataFrame(columns={"year": lu_list[0]["year"]})
    for e, output in enumerate(lu_list[1:7]):
        kept_columns = output.columns[1:]
        medians = output[kept_columns].mean(axis=1)
        medians_dataframe[categories[e]] = medians

    sum_medians = medians_dataframe[list(medians_dataframe.columns[1:])].sum(axis=1)
    #sum validated
    medians_dataframe = medians_dataframe.div(sum_medians, axis=0)

    # Formatting the data for the stacked plot
    land_uses = []
    for e in range(len(lu_list[1:7])):
        land_uses.append((categories[e], medians_dataframe[categories[e]].tolist()))
    land_uses = dict(land_uses)
    desired_order_list = ["crop_subs", "crop_mark", "fal",  
                          "un", "past", "veg"]
    land_uses = {k: land_uses[k] for k in desired_order_list}
    
    # Plotting
    fig, ax = plt.subplots(figsize =(5, 2))
    #plotting land use data
    ax.stackplot(year, land_uses.values(),
                 labels=land_uses.keys(), alpha=0.8)
    
    #plot tappan data for validation
    ax.bar(val_data["year"], val_data["crop_prop"],
           color="k")
    ax.bar(val_data["year"], val_data["veg_past_prop"],
           color="b", 
           bottom = [1 - val_data.iloc[idx]["veg_past_prop"] for idx in range(len(val_data.index))])
    #figure settings
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    ax.set_title('Evolution of land use')
    ax.set_xlabel('Year')
    ax.set_ylabel('Area (ha)')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    ax.set_xlim([year[0], year[-1]])
    ax.set_ylim([0, 1])
    fig.set_dpi(600)
    plt.title(scale)
    #saving the figure
    if path_results!=None:
        savepath = path_results + "land_use_evolution" + ".svg"
        fig.savefig(savepath, bbox_inches='tight', format='svg')
    plt.show()
    

def plot_input(input_df, name_inputs, scale):
    year = list(set(input_df["year"]))
    
    for name_input in name_inputs:
        plt.plot(year, input_df[name_input], label= name_input)
    plt.title(name_input)
    plt.legend()
    plt.show()


def saturation_frequency(lu_list_list, scales, path_results=None):
    colours = ["#4694a7", "#EE442F"]
    
    fig, ax = plt.subplots(figsize =(9, 2))
    for k, (lu_list, scale) in enumerate(zip(lu_list_list, scales)):
        intensification_df = lu_list[-1].copy()
        
        # Calculating normalized medians
        year = list(set(intensification_df["year"]))
        
        for idx, column in enumerate(intensification_df.columns[1:]):
            intensification_df.columns.values[idx+1] = f"{idx}"
        
        #intensification_df["mean"] = intensification_df.sum(axis=0)
        intensification_df['mean'] = intensification_df.drop(intensification_df.columns[0], axis=1).sum(axis=1)
        intensification_df["mean"] = intensification_df["mean"].div(len(intensification_df.columns)-2)
        
        plt.plot(year, intensification_df["mean"].tolist(), color=colours[k], label=scale)
    plt.ylabel("saturation frequency")
    plt.xlabel("year")
    plt.legend(loc="lower right")
    fig.set_dpi(600)
    plt.show()


def mean_cf(lu_list_list, scales, path_results=None):
    fig, ax = plt.subplots(figsize=(9, 2))
    
    colours_light = ["#63ACBE", "#f48274"]
    colours_dark = ["#4694a7", "#EE442F"]
    
    divergence = [0.2, -0.2]
    
    #medianprops = dict(linewidth=3, color='r')
    for k, (lu_list, scale) in enumerate(zip(lu_list_list, scales)):
        
        subs_df = lu_list[2].copy()
        mark_df = lu_list[3].copy()
        fal_df = lu_list[4].copy()
        
        # calculating the cultivation frequency
        cf_df = pd.DataFrame(columns=["year"])
        cf_df["year"] = subs_df["year"]
        
        for idx in range(len(subs_df.columns)-1):
            cf_df[f"simu_{idx}"] = fal_df.iloc[:, idx+1]
            series_sum = subs_df.iloc[:, idx+1] + mark_df.iloc[:, idx+1]
            cf_df[f"simu_{idx}"] = cf_df[f"simu_{idx}"].div(series_sum)
        cf_df.dropna(axis=1, inplace=True)
        year = list(set(cf_df["year"]))
        year = [int(y) for y in year]
        for i, y in enumerate(year) :
            y+=divergence[k]
            if i!=0:
                series = cf_df.iloc[i, 1:]
                
                
                cl = colours_light[k]
                cd = colours_dark[k]
                
                plt.boxplot(series, positions=[y],
                           patch_artist=True, notch=False,
                           boxprops=dict(facecolor=cl, color=cl, linewidth=2),
                           capprops=dict(color=cl),
                           whiskerprops=dict(color=cl),
                           flierprops=dict(markeredgecolor=cl,
                                           markerfacecolor=cl,
                                           marker="o",
                                           alpha=0.5,
                                           markersize=1.5,
                                           markeredgewidth=0.2),
                           #medianprops=dict(color=c),
                           showfliers=True,

                           medianprops=dict(linewidth=2, color=cd))
                           #label = scale)
    year = list(set(lu_list_list[0][0]["year"]))
    year = [int(y) for y in year]
    #changing ticks
    ticks = np.array(year)
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    #new_ticks = np.delete(new_ticks, np.where(new_ticks%1 != 0))
    ax.set_xticks(new_ticks, new_ticks, rotation=30)
    fig.set_dpi(600)

    plt.ylabel("rotation frequency")
    plt.xlabel("year")
    plt.show()  


        