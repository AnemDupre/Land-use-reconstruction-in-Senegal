# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:19:07 2024

@author: anem
"""

#imports
import core
import numpy as np
import model
import fetch



def generate_parameter_sets(numb, seed):
    """
    Samples parameter sets from the intervals deduced from literature.

    Parameters
    ----------
    numb : INT
        number of parameter sets to generate.
    seed : INT
        seed for reproducibility.

    Returns
    -------
    TYPE
        list of numb parameter sets presented as dictionaries.

    """
    np.random.seed(seed)
    #fetch ranges
    parameter_ranges = fetch.parameter_ranges()
    
    biom_conso_min_range = parameter_ranges["biom_conso_min"]
    biom_conso_max_range = parameter_ranges["biom_conso_max"]
    food_conso_range = parameter_ranges["food_conso"]
    cf_range = parameter_ranges["cf"]
    fuel_conso_rur_range = parameter_ranges["fuel_conso_rur"]
    fuel_conso_urb_range = parameter_ranges["fuel_conso_urb"]
    veg_prod_range = parameter_ranges["veg_prod"]
    a_biom_prod_range = parameter_ranges["a_biom_prod"]
    b_biom_prod_range = parameter_ranges["b_biom_prod"]
    crop_past_ratio_range = parameter_ranges["crop_past_ratio"]

    params_list_rand = []
    for _ in range(numb):
        params = {"biom_conso_min":np.random.uniform(low=biom_conso_min_range[0],
                                                     high=biom_conso_min_range[1]),
                  "biom_conso_max":np.random.uniform(low=biom_conso_max_range[0],
                                                     high=biom_conso_max_range[1]),
                  "food_conso":np.random.uniform(low=food_conso_range[0],
                                                 high=food_conso_range[1]),
                  "cf":np.random.uniform(low=cf_range[0],
                                         high=cf_range[1]),
                  "fuel_conso_rur":np.random.uniform(low=fuel_conso_rur_range[0],
                                                     high=fuel_conso_rur_range[1]),
                  "fuel_conso_urb":np.random.uniform(low=fuel_conso_urb_range[0],
                                                     high=fuel_conso_urb_range[1]),
                  "veg_prod":np.random.uniform(low=veg_prod_range[0],
                                               high=veg_prod_range[1]),
                  "a_biom_prod":np.random.uniform(low=a_biom_prod_range[0],
                                                  high=a_biom_prod_range[1]),
                  "b_biom_prod":np.random.uniform(low=b_biom_prod_range[0],
                                                     high=b_biom_prod_range[1]),
                  "crop_past_ratio":np.random.uniform(low=crop_past_ratio_range[0],
                                                     high=crop_past_ratio_range[1])}

        params_list_rand.append(params)
    return params_list_rand #list of num parameter sets randomely sampled



def iterate_simulation(params_list, area, inputs,
                       preservation, calculate_demand):
    """
    Simulates the land use evolutions of the given parameters sets.
    Results are then extracted, and grouped by ouput type 
    (pastoral land, fallows...).

    Parameters
    ----------
    params_list : LIST OF DICTIONARIES
        Parameter sets we want to use for simulations.
    area : INT or FLOAT
        Surface of the considered region.
    inputs : DATAFRAME
        Contains the inputs of the model: 
            pop_rur, pop_urb, liv, rain, 
            net_imp, yield
            optional: biom_prod.
    preservation : BOOLEAN
        Whether fuelwood extraction areas are protected or not.
    calculate_demand : BOOLEAN
        Whether we output land uses or the demand for lands.

    Returns
    -------
    land_use_list : LIST OF DATAFRAME
        Each dataframe contains the results of all simulations for 
        the given output.

    """
    crop_dfs = []
    past_dfs = []
    crop_subs_dfs = []
    crop_mark_dfs = []
    fal_dfs = []
    un_dfs = []
    veg_dfs = []
    intensification_dfs = []
    biom_prod_dfs = []
    sum_lu_dfs = []

    # launch simulations and extract land use outputs
    for point in params_list:
        land_use_model = model.LandUseModel(area, inputs, params=point,
                                            preservation=preservation,
                                            calculate_demand=calculate_demand)
        land_use_model.iterate()
        crop_df = land_use_model.lu_memory[["year", "crop"]].rename(columns={'crop': 'crop'})
        past_df = land_use_model.lu_memory[["year", "past"]]
        crop_subs_df = land_use_model.lu_memory[["year", "crop_subs"]]
        crop_mark_df = land_use_model.lu_memory[["year", "crop_mark"]]
        fal_df = land_use_model.lu_memory[["year", "fal"]]
        un_df = land_use_model.lu_memory[["year", "un"]]
        veg_df = land_use_model.lu_memory[["year", "veg"]]
        intensification_df = land_use_model.lu_memory[["year", "intensification"]]
        biom_prod_df = land_use_model.biom_prod_memory[["year", "biom_prod"]]
        sum_lu_df = land_use_model.lu_memory[["year", "sum_lu"]]

        #adding the results to the corresponding lists
        crop_dfs.append(crop_df)
        past_dfs.append(past_df)
        crop_subs_dfs.append(crop_subs_df)
        crop_mark_dfs.append(crop_mark_df)
        fal_dfs.append(fal_df)
        un_dfs.append(un_df)
        veg_dfs.append(veg_df)
        intensification_dfs.append(intensification_df)
        biom_prod_dfs.append(biom_prod_df)
        sum_lu_dfs.append(sum_lu_df)

    # Concatenate the lists in a single dataframe for each output
    crop_values = core.merge_df(crop_dfs, column="year")
    past_values = core.merge_df(past_dfs, column="year")
    crop_subs_values = core.merge_df(crop_subs_dfs, column="year")
    crop_mark_values = core.merge_df(crop_mark_dfs, column="year")
    fal_values = core.merge_df(fal_dfs, column="year")
    un_values = core.merge_df(un_dfs, column="year")
    veg_values = core.merge_df(veg_dfs, column="year")
    intensification_values = core.merge_df(intensification_dfs, column="year")
    biom_prod_values = core.merge_df(biom_prod_dfs, column="year")
    sum_lu_values = core.merge_df(sum_lu_dfs, column="year")

    land_use_list = [crop_values, past_values, crop_subs_values,
                     crop_mark_values, fal_values, un_values,
                     veg_values, intensification_values, biom_prod_values,
                     sum_lu_values]

    return land_use_list



def iterate(numb_samples, area, seed, inputs,
            preservation=True, calculate_demand=False):
    """
    Generates the paramer sets samples and calculates associated outputs.

    Parameters
    ----------
    numb_samples : TYPE
        DESCRIPTION.
    area : TYPE
        DESCRIPTION.
    seed : TYPE
        DESCRIPTION.
    inputs : TYPE
        DESCRIPTION.
    preservation : TYPE, optional
        DESCRIPTION. The default is True.
    calculate_demand : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    params_list : TYPE
        DESCRIPTION.
    lu_list : TYPE
        DESCRIPTION.

    """

    #generate parameter sets
    params_list = generate_parameter_sets(numb_samples, seed)
    #simulate land-use evolution
    lu_list = iterate_simulation(params_list, area, inputs, preservation, calculate_demand)

    return params_list, lu_list
