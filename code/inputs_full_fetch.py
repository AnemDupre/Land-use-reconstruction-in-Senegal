# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:08:48 2024

@author: anem
"""
import input_fetch
import core
import pandas as pd
from functools import reduce



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
    
    
    superficies = {"Diourbel": 482400,
                   "Fatick": 684900,
                   "Kaffrine_Kaolack": 1661900,
                   "Thies": 667000} # region surface in ha
    
    #fetching yield and biom_prod
    dic_yield_biom_prod = input_fetch.fetch_simulated_yield_biom_prod(path_to_data)
    #fetching the rest of data
    dic_rest = input_fetch.fetch_other_reg_data(path_to_data + "full_reg_data.xlsx")
    
    #merge
    dic_dfs = {}
    for key in superficies.keys():
        dic_dfs[key] = core.merge_df([dic_yield_biom_prod[key],
                                      dic_rest[key]], column="year")
    
    return superficies, dic_dfs



def combined_reg_full_fetch(path_to_data):
    superficies, inputs_reg_dic = reg_inputs_full_fetch(path_to_data)
    
    combined_df = pd.DataFrame(columns=list(inputs_reg_dic["Diourbel"].columns))
    
    for column in combined_df.columns : 
        if column in ['pop_rur', 'pop_urb', 'net_imp', 'liv']: # extensive variables
            combined_df[column] = reduce(lambda a, b: a.add(b, fill_value=0), 
                              [inputs_reg_dic[region][column] for region in superficies.keys()])
            
        elif column in ["yield", "rain", "biom_prod"]: # intensive variables
            combined_df[column] = reduce(lambda a, b: a.add(b, fill_value=0), 
                              [inputs_reg_dic[region][column] for region in superficies.keys()])
            combined_df[column] = combined_df[column].div(len(superficies.keys()))
            
    combined_df["year"] = inputs_reg_dic["Diourbel"]["year"]
    
    return sum(superficies.values()), combined_df