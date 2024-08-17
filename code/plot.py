# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:17:24 2024

@author: anem
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import fetch



def land_uses_boxplots(lu_list, scale, region_surface, path_results=None):
    """
    For each output land use category, plots the evolution of the 
    percentage of occupied territory in the form of boxplots.

    Parameters
    ----------
    lu_list : TUPLE OF DATAFRAMES
        With dataframes corresponding to each output
        category from the model.
    scale : STR
        Name of considered region.
    region_surface : INT or FLOAT
        Region surface.
    path_results : STR, optional
        Where to save figure. The default is None.

    Returns
    -------
    None.

    """
    #categories of land uses we want to plot
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]
    #properties of boxplot medians
    medianprops = dict(linewidth=3, color='r')
    #generating th figure
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12,15))

    for c, values in enumerate(lu_list[1:7]):
        #enumerating on categories of interest
        
        #choosing the axis on which to plot
        if c<3:
            ax = axes[c][0]
        else:
            ax = axes[c-3][1]

        #formatting our dataframe
        lu_original = values.copy()
        lu_original.reset_index(inplace=True)
        lu_original.set_index('year', inplace=True)
        lu_original.drop("index", axis=1, inplace=True)
        lu_original = lu_original.div(region_surface)
        #calculating the proportion of occupied territory

        #changing column names to be more interpretable
        for count, column in enumerate(lu_original.columns[:]):
            lu_original.rename({column: f'{count}'})

        #plotting
        year = list(set(lu_original.index[:]))
        for i, y in enumerate(year) :
            #for each year plot the boxplot of simulation values
            if i!=0:
                series_or = lu_original.iloc[i]
                ax.boxplot(series_or, positions=[y],
                           showfliers=False,
                           medianprops=medianprops)

        #changing ticks
        ticks = ax.get_xticks()
        ticks = np.array([int(item) for item in ticks])
        new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
        ax.set_xticks(new_ticks, new_ticks, rotation=30)
        ax.set_xlabel('Year')
        ax.set_ylabel(f'{categories[c]} (ha)')
    fig.set_dpi(600)

    #saving the figure
    if path_results!=None:
        save_path = path_results + scale + "_land_uses_boxplots.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    plt.show()



def mean_stack_and_validation(lu_list, scale, path_validation,
                              superficy, path_results=None):
    """
    Plots the means of land use outputs for categories
    "past", "crop_subs", "crop_mark", "fal", "un", "veg".
    Tappan data points are added for validation.

    Parameters
    ----------
    lu_list : TUPLE OF DATAFRAMES
        With dataframes corresponding to each output
        category from the model.
    scale : STR
        Name of considered region.
    path_validation : STR
        Path to Tappan validation data.
    superficy : INT of FLOAT
        Surface of considered region.
    path_results : STR, optional
        Where to save the figure.
        The default is None.

    Returns
    -------
    None.

    """
    #fetching validation data
    val_data = fetch.df(path_validation)
    #name of categories to plot
    categories = ["past", "crop_subs", "crop_mark",
                  "fal", "un", "veg"]

    #calculating means
    means_dataframe = pd.DataFrame(columns={"year": lu_list[0]["year"]})
    for e, output in enumerate(lu_list[1:7]):
        kept_columns = output.columns[1:]
        means = output[kept_columns].mean(axis=1)
        means_dataframe[categories[e]] = means

    # Formatting the data for the stacked plot
    land_uses = []
    for e in range(len(lu_list[1:7])):
        land_uses.append((categories[e],
                          means_dataframe[categories[e]].tolist()))
    land_uses = dict(land_uses)
    desired_order_list = ["crop_subs", "crop_mark", "fal",  
                          "un", "past", "veg"]
    land_uses = {k: land_uses[k] for k in desired_order_list}

    # Plotting
    #choose color style
    plt.style.use('seaborn-v0_8-colorblind')
    #creating the figure
    fig, ax = plt.subplots(figsize =(5, 2))
    #plotting land use data
    year = list(set(lu_list[0]["year"]))
    ax.stackplot(year, land_uses.values(),
                 labels=land_uses.keys(), alpha=0.8)
    #plot tappan data for validation
    crop_bar = ax.bar(val_data["year"], val_data["crop_prop"],
                      edgecolor="w", color="w",
                      hatch="/////", label="croplands")
    #setting hatch color
    for bc in crop_bar:
        bc._hatch_color = mpl.colors.to_rgba("k")
    ax.bar(val_data["year"], val_data["veg_past_prop"],
           color="k", edgecolor="w",
           bottom =  val_data["crop_prop"], 
           label = "forests, steppes, and savannas")
    #plotting the region superficy
    plt.axhline(y=superficy, color = "k", linestyle="dotted")
    #figure settings
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    ax.set_title('Evolution of land use')
    ax.set_xlabel('Year')
    ax.set_ylabel('Area (ha)')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    ax.set_xlim([year[0], year[-1]])
    fig.set_dpi(600)
    plt.title(scale)
    #saving the figure
    if path_results!=None:
        savepath = path_results + f"{scale}_mean_stack" + ".svg"
        fig.savefig(savepath, bbox_inches='tight', format='svg')
    plt.show()



def saturation_frequency(lu_list_list, scales, path_results=None):
    
    #colours associated with scales "Senegal" and "Groundnut basin"
    colours = ["#4694a7", "#EE442F"]

    #Generating the figure
    fig, ax = plt.subplots(figsize =(9, 2))
    for k, (lu_list, scale) in enumerate(zip(lu_list_list, scales)):
        intensification_df = lu_list[7].copy()
        
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



def plot_input(input_df, name_inputs, scale):
    year = list(set(input_df["year"]))
    
    for name_input in name_inputs:
        plt.plot(year, input_df[name_input], label= name_input)
    plt.title(name_input)
    plt.legend()
    plt.show()



def rotation_frequency(lu_list_list, scales, path_results=None):
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



def all_inputs(inputs_nat, inputs_reg, 
               superficy_nat, superficy_reg, 
               lu_list_nat, lu_list_reg,
               path_results=None):
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1, 
                                    figsize=(7,7),
                                    gridspec_kw={'height_ratios': [3,1,1,2,1]},
                                    sharex=True)
    superficies = [superficy_nat, superficy_reg]
    
    
    colours_light = ["#63ACBE", "#f48274"]
    colours_dark = ["#4694a7", "#EE442F"]
    for k, inputs_df in enumerate([inputs_nat, inputs_reg]):
            year = list(set(inputs_df["year"]))
            
            
            #demography
            rur, = ax1.plot(year, inputs_df["pop_rur"].div(superficies[k]), color=colours_dark[k], linewidth=2,
                     label="rural population")
            urb, = ax1.plot(year, inputs_df["pop_urb"].div(superficies[k]), color=colours_dark[k], linewidth=2,
                     label="urban population", linestyle="dashed")
            ax1.set_ylabel('Demography\n(inhab/ha/year)')

            #livestock
            ax2.plot(year, inputs_df["liv"].div(superficies[k]), color=colours_dark[k], linewidth=2)
            ax2.set_ylabel('Livestock\n(TLU/ha/year)')
        

    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    ax1.legend(handles=[rur, urb])
    
    
    #yield
    ax3.plot(inputs_nat["year"], inputs_nat["yield"].div(1000), color=colours_dark[0], linewidth=2,
             label="Senegal")
    ax3.plot(inputs_reg["year"], inputs_reg["yield"].div(1000), color=colours_dark[1], linewidth=2,
             label="Groundnut bassin")
    ax3.set_ylabel('Yield\n(tonnes/ha/year)')
    ax3.legend(loc="upper left")
    
    #plot biom_prod
    year = list(set(lu_list_nat[-2]["year"]))
    for i, y in enumerate(year) :
        if i!=0:
            series = lu_list_nat[-2].iloc[i, 1:]
                
            cl = colours_light[0]
            cd = colours_dark[0]
                    
            ax4.boxplot(series, positions=[y],
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
                        showfliers=True,
                        medianprops=dict(linewidth=2, color=cd))
    ax4.plot(lu_list_reg[-2]["year"], lu_list_reg[-2].iloc[:, 1],
             color = colours_dark[1])
    ax4.set_ylabel('Biomass productivity\n (tonnes/ha/year)')
    ax4.yaxis.set_label_position("right")
    ax4.yaxis.tick_right()

    
    #cereal imports
    ax5.plot(inputs_nat["year"], inputs_nat["net_imp"].div(inputs_nat["pop_urb"]), 
                     color="k", linewidth=2)
    ax5.set_ylabel('Cereal imports\n(Tonnes/urban inhab/year)')
    ax5.set_xlabel('Year')

    #changing ticks
    ticks = ax5.get_xticks()
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    #new_ticks = np.delete(new_ticks, np.where(new_ticks%1 != 0))
    ax5.set_xticks(new_ticks, new_ticks, rotation=30)
    ax5.set_xlim([1960,2021])
    if path_results!=None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    fig.set_dpi(600)
    plt.show()



def past_pressure(lu_list, inputs, params_list, path_results=None):
    years = list(set(inputs["year"]))
    liv = inputs["liv"]    
    past_df = lu_list[1].copy()
    #changing column names to be more interpretable
    past_df.columns = ["year"] +\
        [f'{idx}' for idx in range(len(past_df.columns)-1)]
    print(past_df)
    
    biom_prod_df = lu_list[8].copy()
    #biom_prod_df.colums = list(past_df.columns)
    biom_prod_df = biom_prod_df.set_axis(list(past_df.columns), axis=1)
    
    percentage_satisf = pd.DataFrame(columns=list(biom_prod_df.columns))
    percentage_satisf["year"] = years
    
    for idx in range(len(params_list)):
        biom_conso = params_list[idx]["biom_conso_max"]
        past_series = past_df[f'{idx}']

        biom_prod_series = biom_prod_df.loc[:,f'{idx}']
        
        prod_series = past_series*biom_prod_series/(3*liv) 
        #dry mass produced by pastoral land (only 1/3 of it is available for livestock consumption)
        
        needs_series = biom_conso/2 #kg of dry matter per day per TLU
        perc_satisf_conso = prod_series/needs_series
        percentage_satisf[f"{idx}"] = perc_satisf_conso
    print(percentage_satisf)

    colours_light = ["#63ACBE", "#f48274"]
    colours_dark = ["#4694a7", "#EE442F"]

    fig, ax = plt.subplots(figsize=(9, 2))
    for i, y in enumerate(years) :
        if i!=0:
            series = percentage_satisf.iloc[i, 1:]
                
            cl = colours_light[0]
            cd = colours_dark[0]
                    
            ax.boxplot(series, positions=[y],
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
                        showfliers=True,
                        medianprops=dict(linewidth=2, color=cd))
        
    #changing ticks
    ticks = ax.get_xticks()
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    #new_ticks = np.delete(new_ticks, np.where(new_ticks%1 != 0))
    ax.set_xticks(new_ticks, new_ticks, rotation=30)
    ax.set_xlim([1960,2021])
    if path_results!=None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    fig.set_dpi(600)
    plt.show()



def intensification_proxys(lu_list, inputs, params_list, path_results = None):
    
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1, 
                                        figsize=(9,6),
                                        sharex=True)
    
    #colours associated with scales "Senegal" and "Groundnut basin"
    light = "#63ACBE"
    dark = "#4694a7"
    #Generating the figure
    
    # Territory saturation

    intensification_df = lu_list[7].copy()
    year = list(set(intensification_df["year"]))
    year = [int(y) for y in year]
    # Calculating normalized medians
    for idx, column in enumerate(intensification_df.columns[1:]):
        intensification_df.columns.values[idx+1] = f"{idx}"
        
    #intensification_df["mean"] = intensification_df.sum(axis=0)
    intensification_df['mean'] = intensification_df.drop(intensification_df.columns[0], axis=1).sum(axis=1)
    intensification_df["mean"] = intensification_df["mean"].div(len(intensification_df.columns)-2)
        
    ax1.plot(year, intensification_df["mean"].tolist(),
             color=dark)
    ax1.set_ylabel("saturation\nfrequency")
    ax1.set_xlim([1960,2021])

    new_ticks = np.array([0.0, 0.5, 1.0])
    ax1.set_yticks(new_ticks, new_ticks)

    # Cultivation frequency
    
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

    for i, y in enumerate(year) :
        if i!=0:
            series = cf_df.iloc[i, 1:]
            ax2.boxplot(series, positions=[y],
                        patch_artist=True, notch=False,
                        boxprops=dict(facecolor=light, color=light, linewidth=2),
                        capprops=dict(color=light),
                        whiskerprops=dict(color=light),
                        flierprops=dict(markeredgecolor=light,
                                           markerfacecolor=light,
                                           marker="o",
                                           alpha=0.5,
                                           markersize=1.5,
                                           markeredgewidth=0.2),
                        showfliers=True,
                        medianprops=dict(linewidth=2, color=dark))

    ax2.set_ylabel("rotation\nfrequency")
    ax2.set_xlim([1960,2021])

    
    years = list(set(inputs["year"]))
    liv = inputs["liv"]    
    past_df = lu_list[1].copy()
    #changing column names to be more interpretable
    past_df.columns = ["year"] +\
        [f'{idx}' for idx in range(len(past_df.columns)-1)]
    
    biom_prod_df = lu_list[8].copy()
    #biom_prod_df.colums = list(past_df.columns)
    biom_prod_df = biom_prod_df.set_axis(list(past_df.columns), axis=1)
    
    percentage_satisf = pd.DataFrame(columns=list(biom_prod_df.columns))
    percentage_satisf["year"] = years
    
    for idx in range(len(params_list)):
        biom_conso = params_list[idx]["biom_conso_max"]
        past_series = past_df[f'{idx}']

        biom_prod_series = biom_prod_df.loc[:,f'{idx}']
        
        prod_series = past_series*biom_prod_series/(3*liv) 
        #dry mass produced by pastoral land (only 1/3 of it is available for livestock consumption)
        
        needs_series = biom_conso/2 #kg of dry matter per day per TLU
        perc_satisf_conso = prod_series/needs_series
        percentage_satisf[f"{idx}"] = perc_satisf_conso

    for i, y in enumerate(years) :
        if i!=0:
            series = percentage_satisf.iloc[i, 1:]
                    
            ax3.boxplot(series, positions=[y],
                        patch_artist=True, notch=False,
                        boxprops=dict(facecolor=light, color=light, linewidth=2),
                        capprops=dict(color=light),
                        whiskerprops=dict(color=light),
                        flierprops=dict(markeredgecolor=light,
                                            markerfacecolor=light,
                                            marker="o",
                                            alpha=0.5,
                                            markersize=1.5,
                                            markeredgewidth=0.2),
                        showfliers=True,
                        medianprops=dict(linewidth=2, color=dark))
    ax3.set_ylabel("satisfied\nconsumption (%)")
    #changing ticks
    ticks = ax3.get_xticks()
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    ax3.set_xticks(new_ticks, new_ticks, rotation=30)
    ax3.set_xlim([1960,2021])
    ax3.set_xlabel("year")
    
    fig.align_ylabels()
    
    if path_results!=None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    fig.set_dpi(600)
    plt.show()