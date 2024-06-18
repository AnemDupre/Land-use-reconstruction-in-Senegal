# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:33:34 2024

@author: anem
"""

import pandas as pd
import merge

def fetch_temp_and_perm_crop(path):
    # Population data
    df = pd.read_excel(path) #charger le fichier Excel dans un DataFrame
    temp_crop = df[df['Item'] == 'Temporary crops'][["Year", "Value"]]
    temp_crop = temp_crop.rename(columns = {'Value':'temp_crop'})
    temp_crop['temp_crop'] = temp_crop['temp_crop'].apply(lambda x: x*1000)
    perm_crop = df[df['Item'] == 'Permanent crops'][["Year", "Value"]]
    perm_crop = perm_crop.rename(columns = {'Value':'perm_crop'})
    perm_crop['perm_crop'] = perm_crop['perm_crop'].apply(lambda x: x*1000)
    #we want the population to be in number of inhabitants not in 1000 inhabitants
    crop_df = merge.merge_df([temp_crop, perm_crop])
    crop_df["crop_fao"] = crop_df["temp_crop"] + crop_df["perm_crop"]
    crop_df = crop_df.rename(columns = {'Year':'year'})
    return crop_df

def fetch_fal(path):
    # fao fallow data
    df = pd.read_excel(path)
    fal = df[["Year", "Value"]].copy()
    fal['Value'] = fal['Value'].apply(lambda x: x*1000)
    fal = fal.rename(columns = {'Year':'year', 'Value':'fal_fao'})
    return fal

def fetch_past(path):
    # fao fallow data
    df = pd.read_excel(path)
    past = df[["Year", "Value"]].copy()
    past['Value'] = past['Value'].apply(lambda x: x*1000)
    past = past.rename(columns = {'Year':'year', 'Value':'past_fao'})
    return past

def fetch_veg(path):
    # fao fallow data
    df = pd.read_excel(path)
    veg = df[["Year", "Value"]].copy()
    veg['Value'] = veg['Value'].apply(lambda x: x*1000)
    veg = veg.rename(columns = {'Year':'year', 'Value':'veg_fao'})
    return veg

def fetch_1_column(path, name, new_name=None):
    df = pd.read_excel(path)
    df_extract = df[[name]].copy()
    if new_name!=None:
        df_extract = df_extract.rename(columns = {name:new_name})
    return df_extract

def fetch_multi_columns(path, names, new_names=None):
    df = pd.read_excel(path) 
    df_extract = df[names].copy()
    if new_names!=None:
        df_extract = df_extract.rename(columns = dict(zip(names, new_names)))
    return df_extract