# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:08:48 2024

@author: anem
"""
import input_fetch
import core
import pandas as pd

def nat_inputs_full_fetch(path_to_data, country, NAT_AREA, rain_data_source, 
                      file_pop="pop_rur_pop_urb.xlsx", file_animals="animals.xlsx",
                      file_cereals="cereal_imports_exports.xlsx", file_yield="crop_yield_fao_raw.xlsx"):

    path_to_data+="inputs\\"
    [path_pop, path_animals, path_cereals, path_yield] = list(map(lambda name: path_to_data + name,
                                                                                 [file_pop, file_animals, file_cereals, file_yield]))
    pop_df = input_fetch.fetch_pop(path_pop)
    animals_df = input_fetch.fetch_animals(path_animals)
    rain_df = input_fetch.fetch_rain(path_to_data, NAT_AREA, data=rain_data_source)
    cereals_df = input_fetch.fetch_cereal_net_imp(path_cereals)
    yield_df = input_fetch.fetch_crop_yield(path_yield, country)
    combined_df = core.merge_df([pop_df, animals_df, rain_df, cereals_df, yield_df])
    combined_df = combined_df.rename(columns = {'Year':'year'})
    combined_df = combined_df.dropna() #we only want years for which we have data for all variables
    #input_fetch.add_liv_column(combined_df)

    return combined_df



def reg_inputs_full_fetch(path_to_data):
    path_to_data+="inputs\\"
    dic_dfs = {}
    
    superficies = {"Diourbel": 482400,
                   "Fatick": 684900,
                   "Kaffrine_Kaolack": 1661900,
                   "Thies": 667000} # region surface in ha
    
    path_precessed_data = path_to_data + "full_reg_data.xlsx"
    xls = pd.ExcelFile(path_precessed_data)
    #biomass = path_to_data +
    
    for region in superficies.keys():
        df_region = pd.read_excel(xls, region)
        df_region.dropna(how='any')
        dic_dfs[region] = df_region
    
    return superficies, dic_dfs
    
    
    
    