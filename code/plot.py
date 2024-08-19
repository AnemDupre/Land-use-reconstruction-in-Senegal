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
import seaborn as sns
import matplotlib.colors as mcolors



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

    #generating th figure
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12,15))

    for category_idx, values in enumerate(lu_list[1:7]):
        #enumerating on categories of interest

        #choosing the axis on which to plot
        if category_idx<3:
            axis = axes[category_idx][0]
        else:
            axis = axes[category_idx-3][1]

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
        years = list(set(lu_original.index[:]))
        for i, year in enumerate(years) :
            #for each year plot the boxplot of simulation values
            if i!=0:
                axis.boxplot(lu_original.iloc[i], positions=[year],
                             showfliers=False,
                             medianprops={"linewidth":3,
                                          "color":'r'}
                             #properties of boxplot medians
                             )

        #changing ticks
        new_ticks = axis.get_xticks()
        new_ticks = np.array([int(item) for item in new_ticks])
        new_ticks = np.delete(new_ticks, np.where(new_ticks%10 != 0))
        axis.set_xticks(new_ticks, new_ticks, rotation=30)
        axis.set_xlabel('Year')
        axis.set_ylabel(f'{categories[category_idx]} (ha)')
    fig.set_dpi(600)

    #saving the figure
    if path_results is not None:
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
    for count, output in enumerate(lu_list[1:7]):
        kept_columns = output.columns[1:]
        means = output[kept_columns].mean(axis=1)
        means_dataframe[categories[count]] = means

    # Formatting the data for the stacked plot
    land_uses = []
    for category_idx in range(len(lu_list[1:7])):
        land_uses.append((categories[category_idx],
                          means_dataframe[categories[category_idx]].tolist()))
    land_uses = dict(land_uses)
    desired_order_list = ["crop_subs", "crop_mark", "fal",
                          "un", "past", "veg"]
    land_uses = {k: land_uses[k] for k in desired_order_list}

    # Plotting
    #choose color style
    plt.style.use('seaborn-v0_8-colorblind')
    #creating the figure
    fig, axis = plt.subplots(figsize =(5, 2))
    #plotting land use data
    year = list(set(lu_list[0]["year"]))
    axis.stackplot(year, land_uses.values(),
                 labels=land_uses.keys(), alpha=0.8)
    #plot tappan data for validation
    crop_bar = axis.bar(val_data["year"], val_data["crop_prop"],
                      edgecolor="w", color="w",
                      hatch="/////", label="croplands")
    #setting hatch color
    for bc in crop_bar:
        bc._hatch_color = mpl.colors.to_rgba("k")
    axis.bar(val_data["year"], val_data["veg_past_prop"],
           color="k", edgecolor="w",
           bottom =  val_data["crop_prop"],
           label = "forests, steppes, and savannas")
    #plotting the region superficy
    plt.axhline(y=superficy, color = "k", linestyle="dotted")
    #figure settings
    axis.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    axis.set_title('Evolution of land use')
    axis.set_xlabel('Year')
    axis.set_ylabel('Area (ha)')
    axis.legend(loc='center left', bbox_to_anchor=(1, 0.6))
    axis.set_xlim([year[0], year[-1]])
    fig.set_dpi(600)
    plt.title(scale)
    #saving the figure
    if path_results is not None:
        savepath = path_results + f"{scale}_mean_stack" + ".svg"
        fig.savefig(savepath, bbox_inches='tight', format='svg')
    plt.show()



def all_inputs(inputs_list, superficies, lu_lists, path_results=None):
    """
    Plots the input time series of national and regional scales,
    displayed per unit space.

    Parameters
    ----------
    inputs_list : LIST OF DATAFRAMES
        Contains the input time series of national and reional scales.
    superficies : LIST OF INT OR FLOAT
        National and regional areas.
    lu_lists : LIST OF TUPLES OF DATAFRAMES
        Model outputs for each scale.
    path_results : STR, optional
        Where to save the figure. The default is None.

    Returns
    -------
    None.

    """
    #colours for plotting
    colours_light = ["#63ACBE", "#f48274"]
    colours_dark = ["#4694a7", "#EE442F"]

    #generating the figure
    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(nrows=5, ncols=1,
                                    figsize=(7,7),
                                    gridspec_kw={'height_ratios': [3,1,1,2,1]},
                                    sharex=True)

    #plotting population density and livestock density
    for k, inputs_df in enumerate(inputs_list):
        year = list(set(inputs_df["year"]))
        #demography
        rur, = ax1.plot(year, inputs_df["pop_rur"].div(superficies[k]),
                        color=colours_dark[k], linewidth=2,
                        label="rural density")
        urb, = ax1.plot(year, inputs_df["pop_urb"].div(superficies[k]),
                        color=colours_dark[k], linewidth=2,
                        label="urban density", linestyle="dashed")
        ax1.set_ylabel('Population density\n(inhab/ha/year)')
        #livestock
        ax2.plot(year, inputs_df["liv"].div(superficies[k]),
                 color=colours_dark[k], linewidth=2)
        ax2.set_ylabel('Livestock density\n(TLU/ha/year)')
    #parametrizing ax1 and ax2
    ax1.legend(handles=[rur, urb])
    #putting ylabels and ticks on the right
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()

    #plotting yield
    ax3.plot(inputs_list[0]["year"], inputs_list[0]["yield"].div(1000),
             color=colours_dark[0], linewidth=2,
             label="Senegal")
    ax3.plot(inputs_list[1]["year"], inputs_list[1]["yield"].div(1000),
             color=colours_dark[1], linewidth=2,
             label="Groundnut bassin")
    ax3.set_ylabel('Crop yield\n(tonnes/ha/year)')
    ax3.legend(loc="upper left")

    #plotting biom_prod
    years = list(set(lu_lists[0][-2]["year"]))
    for i, year in enumerate(years) :

        series = lu_lists[0][-2].iloc[i, 1:]

        colour_light = colours_light[0]
        colour_dark = colours_dark[0]

        ax4.boxplot(series, positions=[year],
                    patch_artist=True, notch=False,
                    boxprops={"facecolor":colour_light,
                              "color":colour_light,
                              "linewidth":2},
                    capprops={"color":colour_light},
                    whiskerprops={"color":colour_light},
                    flierprops={"markeredgecolor":colour_light,
                                "markerfacecolor":colour_light,
                                "marker":"o",
                                "alpha":0.5,
                                "markersize":1.5,
                                "markeredgewidth":0.2},
                    showfliers=True,
                    medianprops={"linewidth":2,
                                 "color":colour_dark}
                    )
    ax4.plot(lu_lists[1][-2]["year"], lu_lists[1][-2].iloc[:, 1],
             color = colours_dark[1])
    ax4.set_ylabel('Rangeland productivity\n(tonnes/ha/year)')
    ax4.yaxis.set_label_position("right")
    ax4.yaxis.tick_right()

    #plotting cereal imports
    ax5.plot(inputs_list[0]["year"],
             inputs_list[0]["net_imp"].div(inputs_list[0]["pop_urb"]),
             color="k", linewidth=2)
    ax5.set_ylabel('Cereal imports\n(Tonnes/urban inhab/year)')
    ax5.set_xlabel('Year')

    #Parametrizing ticks
    ticks = ax5.get_xticks()
    ticks = np.array([int(item) for item in ticks])
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    ax5.set_xticks(new_ticks, new_ticks, rotation=30)
    ax5.set_xlim([1960,2021])

    #saving the figure
    if path_results is not None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    fig.set_dpi(600)
    plt.show()



def intensification_proxys(lu_list, inputs, params_list, path_results = None):
    """
    Plots the intensification proxys : territory saturation frequency,
    cultivation frequency, and percentage of livestock consumption
    satisfied by pasture.

    Parameters
    ----------
    lu_list : TUPLE OF DATAFRAMES
        With dataframes corresponding to each output
        category from the model.
    inputs : DATAFRAME
        Contains the input time series.
    params_list : LIST OF DICTIONARIES
        Contains the parameter sets used for
        each simulation in lu_list.
    path_results : STR, optional
        Where to save the figure if desired. The default is None.

    Returns
    -------
    None.

    """
    #colours associated with scales "Senegal" and "Groundnut basin"
    light = "#63ACBE"
    dark = "#4694a7"
    #Generating the figure
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, ncols=1,
                                        figsize=(9,6),
                                        sharex=True)

    # Territory saturation
    intensification_df = lu_list[7].copy() #fetching the dataframe
    #defining the year series for the whole figure
    years = list(set(intensification_df["year"]))
    years = [int(y) for y in years]
    #changing the column names to manipulate them more easily
    for idx, _ in enumerate(intensification_df.columns[1:]):
        intensification_df.columns.values[idx+1] = f"{idx}"
    #calculating the mean intensification value for all years
    intensification_df['mean'] = intensification_df.drop(intensification_df.columns[0],
                                                         axis=1).sum(axis=1)
    intensification_df["mean"] = intensification_df["mean"].div(len(intensification_df.columns)-2)
    #plotting saturation frequency
    ax1.plot(years, intensification_df["mean"].tolist(),
             color=dark)
    #display parameters
    ax1.set_ylabel("Saturation\nfrequency")
    ax1.set_xlim([1960,2021])
    new_ticks = np.array([0.0, 0.5, 1.0])
    ax1.set_yticks(new_ticks, new_ticks) #changing ticks

    # Cultivation frequency
    #fetching data
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
    #plotting the cultivation frequency
    for i, year in enumerate(years) :
        series = cf_df.iloc[i, 1:]
        ax2.boxplot(series, positions=[year],
                    patch_artist=True, notch=False,
                    boxprops={"facecolor":light,
                              "color":light,
                              "linewidth":2},
                    capprops={"color":light},
                    whiskerprops={"color":light},
                    flierprops={"markeredgecolor":light,
                                "markerfacecolor":light,
                                "marker":"o",
                                "alpha":0.5,
                                "markersize":1.5,
                                "markeredgewidth":0.2},
                    showfliers=True,
                    medianprops={"linewidth":2,
                                 "color":dark}
                    )
    #display parameters
    ax2.set_ylabel("Cultivation\nfrequency")
    ax2.set_xlim([1960,2021])

    # Satisfied percentage of livestock consumption
    #fetching data
    liv = inputs["liv"]
    past_df = lu_list[1].copy()
    #changing column names to be more interpretable
    past_df.columns = ["year"] +\
        [f'{idx}' for idx in range(len(past_df.columns)-1)]
    biom_prod_df = lu_list[8].copy()
    biom_prod_df = biom_prod_df.set_axis(list(past_df.columns), axis=1)
    #calculating satisfied consumption
    percentage_satisf = pd.DataFrame(columns=list(biom_prod_df.columns))
    percentage_satisf["year"] = years
    for idx, params in enumerate(params_list):
        #fetching data specific to that simulation
        biom_conso = params["biom_conso_max"]
        past_series = past_df[f'{idx}']
        biom_prod_series = biom_prod_df.loc[:,f'{idx}']
        #calculating
        prod_series = past_series*biom_prod_series/(3*liv)
        #dry mass produced by pastoral land
        #(only 1/3 of it is available for livestock consumption)
        needs_series = biom_conso/2
        #tonnes of dry matter needed per TLU per year
        perc_satisf_conso = prod_series/needs_series
        percentage_satisf[f"{idx}"] = perc_satisf_conso
    #plotting satisfied consumption
    for i, year in enumerate(years) :
        series = percentage_satisf.iloc[i, 1:]
        ax3.boxplot(series, positions=[year],
                    patch_artist=True, notch=False,
                    boxprops={"facecolor":light,
                              "color":light,
                              "linewidth":2},
                    capprops={"color":light},
                    whiskerprops={"color":light},
                    flierprops={"markeredgecolor":light,
                                "markerfacecolor":light,
                                "marker":"o",
                                "alpha":0.5,
                                "markersize":1.5,
                                "markeredgewidth":0.2},
                    showfliers=True,
                    medianprops={"linewidth":2,
                                 "color":dark}
                    )
    ax3.set_ylabel("Satisfied\nconsumption (%)")

    #changing ticks
    ticks = ax3.get_xticks()
    new_ticks = np.delete(ticks, np.where(ticks%10 != 0))
    ax3.set_xticks(new_ticks, new_ticks, rotation=30)
    ax3.set_xlim([1960,2021])
    ax3.set_xlabel("Year")
    fig.align_ylabels()

    #saving the figure
    if path_results is not None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    fig.set_dpi(600)
    plt.show()



# Define a custom colormap
def create_custom_cmap(threshold, low_color, mid_color, high_color):
    """
    Create a custom colormap with a specific threshold.
    
    Parameters:
        threshold (float): The value below which the colormap transitions to blue.
        low_color (str): The color for values below the threshold.
        mid_color (str): The color for values at the threshold.
        high_color (str): The color for values above the threshold.
    
    Returns:
        LinearSegmentedColormap: The custom colormap.
    """
    # Define color transitions
    colors = [
        low_color, # Color for values below the threshold
        mid_color,  # Transition color at the threshold
        high_color  # Color for values above the threshold
        
                
    ]
    
    # Define color positions
    positions = [0, threshold, 1.0]
    
    # Create a colormap with these colors and positions
    cmap = mcolors.LinearSegmentedColormap.from_list("cool", list(zip(positions, colors)))
    return cmap



def sensitivity_heatmap(delta_results, path_results=None):
    output_items = ["past", "crop_subs", "crop_mark",
                    "fal", "un", "veg", "mean"]
    #get delta values
    delta_matrix = np.array([df["delta"] for df in delta_results]).T
    #add mean column
    delta_matrix = np.hstack((delta_matrix,
                              delta_matrix.mean(axis=1)[:, np.newaxis]))

    # Convert to DataFrame
    df = pd.DataFrame(delta_matrix, columns=output_items,
                      index=fetch.parameter_ranges().keys())

    # Sort DataFrame by a specific column (e.g., 'Output 2')
    df = df.sort_values(by='mean', ascending=False)
    
    # Specify the column to exclude from sorting
    column_to_exclude = 'mean'

    # Calculate the mean of each column, excluding the specified column
    column_means = df.drop(columns=[column_to_exclude]).mean()

    # Sort columns based on their mean values (excluding the specified column)
    sorted_columns = column_means.sort_values(ascending=False).index

    # Reconstruct the column order, placing the excluded column at its original position
    reordered_columns = list(sorted_columns)  # Start with sorted columns
    reordered_columns.insert(df.columns.get_loc(column_to_exclude), column_to_exclude)  # Insert excluded column at its original position

    # Reorder the DataFrame according to the new column order
    df_sorted = df[reordered_columns]

    #cmap = sns.diverging_palette(240, 10, n=256, center="dark", as_cmap=True)
    #cmap = sns.diverging_palette(240, 20, s=90, l=50, n=256, as_cmap=True, center='light')
    
    # Create a colormap with blue starting below 0.1
    threshold = 0.1
    low_color = 'white'
    mid_color = 'pink'
    high_color = 'red'
    cmap = create_custom_cmap(threshold, low_color, mid_color, high_color)
    # Create a heatmap using seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(df_sorted, annot=True, cmap=cmap)
                #center=np.median(delta_matrix))

    #for i in range(df_sorted.shape[0]):
    ax.add_patch(plt.Rectangle((6, 0),
                               1, 10,
                               color='black',
                               fill=False,
                               linewidth=1,
                               zorder=1))

    plt.title('Heatmap of Delta Indices for Parameters')
    plt.xlabel('Output Dimensions')
    plt.ylabel('Parameters')
    fig.set_dpi(600)

    #saving the figure
    if path_results is not None:
        save_path = path_results + "no_scatter.svg"
        fig.savefig(save_path, bbox_inches='tight', format='svg')

    plt.show()
