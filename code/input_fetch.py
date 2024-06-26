# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 12:44:20 2024

@author: anem
"""

import pandas as pd
import os.path
import core



def fetch_pop(path):
    # Population data
    df = pd.read_excel(path) #charger le fichier Excel dans un DataFrame
    pop_rur = df[df['Element'] == 'Rural population'][["Year", "Value"]]
    pop_rur = pop_rur.rename(columns = {'Value':'pop_rur'})
    pop_rur['pop_rur'] = pop_rur['pop_rur'].apply(lambda x: x*1000)
    pop_urb = df[df['Element'] == 'Urban population'][["Year", "Value"]]
    pop_urb = pop_urb.rename(columns = {'Value':'pop_urb'})
    pop_urb['pop_urb'] = pop_urb['pop_urb'].apply(lambda x: x*1000)
    #we want the population to be in number of inhabitants not in 1000 inhabitants
    
    return core.merge_df([pop_rur, pop_urb])



def fetch_rain(path_to_data, NAT_AREA, data="World_bank"):
    if data=="world_bank" :
        rain = pd.read_excel(path_to_data + "rain_world_bank.xlsx")
        # Rain data
        rain = rain.rename(columns = {'Annual mean':'rain'})
    elif data=="era" :
        if os.path.exists(path_to_data + "rain_ERA5_preprocessed.xlsx"): #the data has already been processed we just need to retrieve it
            rain = pd.read_excel(path_to_data + "rain_ERA5_preprocessed.xlsx")
        else : #we need to precess the data
            rain = pd.read_excel(path_to_data + "rain_ERA5.xlsx")
            rain = rain[["Time","Precipitation (kg m-2 s-1)"]]
            #converting to mm/hour
            rain['Precipitation (kg m-2 s-1)'] = rain['Precipitation (kg m-2 s-1)'].apply(lambda x: x*3600)#*NAT_AREA*10000)
            #rain['Year'] = rain['Year'].dt.strftime('%Y') #converting DateTime data to string
            rain.Time = rain.Time.dt.strftime('%Y')
            rain.Time = rain.Time.apply(int)
            rain = rain.groupby('Time', as_index=False).sum()
            rain = rain.rename(columns = {'Time':'Year','Precipitation (kg m-2 s-1)':'rain'})
            rain.to_excel(path_to_data + "rain_ERA5_preprocessed.xlsx", index=False)
    elif data=="crudata":
        rain = pd.read_excel(path_to_data + "rain_crudata_preprocessed.xlsx")
    elif data=="era_wb":
        if os.path.exists(path_to_data + "rain_era5_wb_preprocessed.xlsx"): #the data has already been processed we just need to retrieve it
            rain = pd.read_excel(path_to_data + "rain_era5_wb_preprocessed.xlsx")
        else:
            rain = pd.read_excel(path_to_data + "rain_era5_wb_raw.xlsx")
            rain = rain.T.iloc[2:] #transposing the data
            rain = rain.reset_index() #we don't want the years to be the index
            rain = rain.rename(columns = {'index':'Year', 0:'rain'})
            rain.Year = rain.Year.apply(lambda x: int(x[:4]))
            rain = rain.groupby('Year', as_index=False).sum()
            rain.to_excel(path_to_data + "rain_era5_wb_preprocessed.xlsx", index=False)
    #rain = rain.rename(columns={"Year":"year"})
    return rain



def fetch_cereal_net_imp(path):
    df = pd.read_excel(path)
    
    #extracting cereal import/export values
    imp_cereal = df[(df['Element'] == 'Import Quantity') &
                  (df['Item'] == 'Cereals')][["Year", "Value"]]
    imp_cereal = imp_cereal.rename(columns = {'Value':'imp_cereal'})
    exp_cereal = df[(df['Element'] == 'Export Quantity') &
                  (df['Item'] == 'Cereals')][["Year", "Value"]]
    exp_cereal = exp_cereal.rename(columns = {'Value':'exp_cereal'})
    
    #extracting cereal preparation values
    imp_cereal_prep = df[(df['Element'] == 'Import Quantity') &
                  (df['Item'] == 'Cereal preparations total')][["Year", "Value"]]
    imp_cereal_prep = imp_cereal_prep.rename(columns = {'Value':'imp_cereal_prep'})
    exp_cereal_prep = df[(df['Element'] == 'Export Quantity') &
                  (df['Item'] == 'Cereal preparations total')][["Year", "Value"]]
    exp_cereal_prep = exp_cereal_prep.rename(columns = {'Value':'exp_cereal_prep'})
    
    #creating a dataframe with all extracted components
    exp_imp = core.merge_df([imp_cereal, exp_cereal, imp_cereal_prep, exp_cereal_prep])
    exp_imp["net_imp"] = (exp_imp["imp_cereal"] + exp_imp["imp_cereal_prep"]) -\
        (exp_imp["exp_cereal"] + exp_imp["exp_cereal_prep"])

    return exp_imp[["Year", "net_imp"]]



def fetch_crop_yield(path_yield, country):
    if country=="Burkina_Faso":
        country="Burkina Faso"
    
    crop_yield = pd.read_excel(path_yield)
    crop_yield.columns = crop_yield.iloc[2] #replacing default column names by the actual categories in the document
    crop_yield = crop_yield.iloc[3:]
    
    country_crop_yield = crop_yield.loc[crop_yield['Country Name'] == country]
    country_crop_yield = country_crop_yield.T.iloc[5:].reset_index()
    country_crop_yield = country_crop_yield.rename(columns = {country_crop_yield.columns[0]:'Year',
                                                              country_crop_yield.columns[1]:'yield'})
    return country_crop_yield



def calculate_liv(camels, cattle, horses,
                  asses, goats, sheep,
                  TLU_EQ_CAMELS=1, TLU_EQ_CATTLE=1,
                  TLU_EQ_HORSES=1, TLU_EQ_ASSES=5,
                  TLU_EQ_GOATS=10, TLU_EQ_SHEEP=10):
    """
    

    Parameters
    ----------
    Camels : TYPE
        DESCRIPTION.
    Cattle : TYPE
        DESCRIPTION.
    Horses : TYPE
        DESCRIPTION.
    Asses : TYPE
        DESCRIPTION.
    Goats : TYPE
        DESCRIPTION.
    TLU_EQ_CAMELS : INT, optional
        DESCRIPTION. The default is 1.
    TLU_EQ_CATTLE : TYPE, optional
        DESCRIPTION. The default is 1.
    TLU_EQ_HORSES : TYPE, optional
        DESCRIPTION. The default is 1.
    TLU_EQ_ASSES : TYPE, optional
        DESCRIPTION. The default is 5.
    TLU_EQ_GOATS : TYPE, optional
        DESCRIPTION. The default is 10.

    Returns
    -------
    Liv : TYPE
        DESCRIPTION.

    """
    liv = camels/TLU_EQ_CAMELS + cattle/TLU_EQ_CATTLE + \
            horses/TLU_EQ_HORSES + asses/TLU_EQ_ASSES + \
                goats/TLU_EQ_GOATS + sheep/TLU_EQ_SHEEP
    return liv



def fetch_animals(path):
    # Animal data
    df = pd.read_excel(path)
    asses = df[df['Item'] == 'Asses'][["Year", "Value"]]
    asses = asses.rename(columns = {'Value':'asses'})
    camels = df[df['Item'] == 'Camels'][["Year", "Value"]]
    camels = camels.rename(columns = {'Value':'camels'})
    cattle = df[df['Item'] == 'Cattle'][["Year", "Value"]]
    cattle = cattle.rename(columns = {'Value':'cattle'})
    goats = df[df['Item'] == 'Goats'][["Year", "Value"]]
    goats = goats.rename(columns = {'Value':'goats'})
    horses = df[df['Item'] == 'Horses'][["Year", "Value"]]
    horses = horses.rename(columns = {'Value':'horses'})
    sheep = df[df['Item'] == 'Sheep'][["Year", "Value"]]
    sheep = sheep.rename(columns = {'Value':'sheep'})
    
    animals = core.merge_df([asses, camels, cattle, goats, horses, sheep])
    animals["liv"] = calculate_liv(camels=animals["camels"],
                                   cattle=animals["cattle"],
                                   horses=animals["horses"],
                                   asses=animals["asses"],
                                   goats=animals["goats"],
                                   sheep=animals["sheep"])
    return animals