# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 09:23:38 2024

@author: anem

This file contains the two classes allowing for calculation
of land use. The first class is the LandUseCalculator that
handles all calculation for a given year. The second class,
the LandUseModel, handles the feeding of data into the
landUseCalculator for all available years and saves results
so that they are easily accessible.

"""

import pandas as pd



class LandUseModel:
    def __init__(self, area, exogenous_df,
                 calculate_demand=False, params=None):
        #initializing the land use calculator with area and data from the frst year
        self.land_use_calculator = LandUseCalculator(area, exogenous_df.iloc[0], params=params)
        self.exogenous_df = exogenous_df
        self.calculate_demand = calculate_demand

        #initilizing dataframes to keep results from each step

        #for land use
        self.lu_memory = pd.DataFrame(columns=['year',
                                               'past',
                                               'crop',
                                               'crop_subs',
                                               'crop_mark',
                                               'fal',
                                               'un',
                                               'veg_d',
                                               'veg',
                                               'intensification'])
        #to keep track of inputs
        self.biom_prod_memory = pd.DataFrame(columns=["year",
                                                      "biom_prod"])



    def iterate(self):
        """
        Injects the exogenous variables into the
        land_use_calculator for each year in the
        exogenous dataframe. Then saves the results
        into the lu_state and endo_state.

        Returns
        -------
        None.

        """
        for index, row in self.exogenous_df.iterrows():
            #calculating land use
            self.land_use_calculator.calculate_land_use(row, self.calculate_demand)

            #saving land use results
            lu_state = pd.DataFrame({"year": [row["year"]],
                                     "past": [self.land_use_calculator.prev_past],
                                     "crop": [self.land_use_calculator.prev_crop],
                                     "crop_subs": [self.land_use_calculator.prev_crop_subs],
                                     "crop_mark": [self.land_use_calculator.prev_crop_mark],
                                     "fal": [self.land_use_calculator.prev_fal],
                                     "un": [self.land_use_calculator.prev_un],
                                     "veg_d":[self.land_use_calculator.veg_d],
                                     "veg":[self.land_use_calculator.prev_veg],
                                     "intensification": [self.land_use_calculator.intensification]})
            self.lu_memory = pd.concat([self.lu_memory, lu_state])

            biom_prod_state = pd.DataFrame({"year": [row["year"]],
                                            "biom_prod": [self.land_use_calculator.biom_prod]})
            self.biom_prod_memory = pd.concat([self.biom_prod_memory,
                                               biom_prod_state])



class LandUseCalculator:
    def __init__(self, area, exogenous, params=None):

        #initializing parameters
        self.area = area #considered region's area [area]=ha

        if params is not None:
            self.biom_conso_min = params["biom_conso_min"]
            self.biom_conso_max = params["biom_conso_max"]
            self.food_conso = params["food_conso"]
            self.cf_init = params["cf"]
            self.fuel_conso_rur = params["fuel_conso_rur"]
            self.fuel_conso_urb = params["fuel_conso_urb"]
            self.veg_prod = params["veg_prod"]
            self.a_biom_prod = params["a_biom_prod"]
            self.b_biom_prod = params["b_biom_prod"]

            if "crop_past_ratio" in params :
                self.crop_past_ratio = params["crop_past_ratio"]
            else :
                self.crop_past_ratio = 2/3

            if "cf_inf" in params:
                self.cf_inf = params["cf_inf"]
            else:
                self.cf_inf = 0
        else: #we take the parameters from the article
            self.biom_conso_min = 2.3
            #minimal biomass consumption during intensification, [biom_conso_min]=tonnes/equivalent TLU
            self.biom_conso_max = 4.6
            #biomass consumption during expansion, [biom_conso_max]=tonnes/equivalent TLU
            self.food_conso = 360 #food consumption [food_conso]=kg/inhab
            self.cf_init = 2 #ideal cultivation frequency (dimensionless)
            self.fuel_conso_rur = 0.65 #rural fuel consumption [fuel_conso_rur]=m3/inhab
            self.fuel_conso_urb = 0.83 #urban fuel consumption [fuel_conso_urb]=m3/inhab
            self.veg_prod = 0.75 #productivity in fuelwood [veg_prod]=m3/ha
            self.a_biom_prod = 0.00375
            self.b_biom_prod = 0.15
            self.crop_past_ratio = 2/3
        #consumption in biomass per head 

        #Initial exogeneous variables
        self.pop_rur = exogenous["pop_rur"] #rural population in inhab
        self.pop_urb = exogenous["pop_urb"] #urban population in inhab
        self.rain = exogenous["rain"] #yearly precipitation in mm
        self.cer_imp = exogenous["net_imp"] #cereal imports in kg
        self.liv = exogenous["liv"] #livestock population in equivalent TLU
        self.crop_yield = exogenous["yield"] #crop yield, [crop_yield]=kg/ha
        if "biom_prod" in exogenous:
            self.biom_prod = exogenous["biom_prod"]
        else:
            self.biom_prod = self.b_biom_prod +\
                self.a_biom_prod*self.rain
            #biomass productivity per year, [biom_prod]=tonnes/ha

        #initializing land demand  (we only need to calculate crop_d and past_d for initialization)
        self.veg_d = 0
        #demand for land destined to fuelwood extraction in ha
        self.crop_subs = self.pop_rur*self.food_conso/self.crop_yield
        #demand for cropland for subsistence agriculture in ha
        self.crop_mark = (self.pop_urb*self.food_conso - self.cer_imp)/self.crop_yield
        #demand for cropland for commercial agriculture in ha
        self.fal_d = self.cf_init*(self.crop_subs + self.crop_mark)
        #demand for land destined to fallow in ha
        self.crop_d = self.crop_subs + self.crop_mark + self.fal_d
        #total demand of cropland in ha
        self.past_d = self.liv*self.biom_conso_max/self.biom_prod
        #pastoral land demand in ha

        #land use of previous state
        self.prev_un = 0 #unused area in ha
        if self.area - self.prev_un - self.past_d - self.crop_d > 0:
            self.prev_veg = self.area - self.prev_un - self.past_d - self.crop_d
            #land covered by natural vegetation (ha)
            self.prev_past = self.past_d #pastoral land (ha)
            self.prev_crop = self.crop_d #cropland (ha)

        else :# we are already in an intensification state
            self.prev_veg = self.area
            self.prev_past = 0 #pastoral land (ha)
            self.prev_crop = 0 #cropland (ha)

        self.prev_fal = 0 #land lying fallow (ha)

        self.prev_crop_subs = 0
        self.prev_crop_mark = 0

        self.land_d = 0 #additional demand for argicultural land relative to the previous year (ha)
        self.intensification = 0 #0: expansion, 1:intensification



    def calculate_demand(self, exogenous):
        """
        Calculates the land demand, that is 
        to say the land needed to satisfy
        the demand in fuelwood, crop and forrage.

        Parameters
        ----------
        exogenous : pd.DataFrame row 
            contains the value of the exogenous
            variables for the year considered.

        Returns
        -------
        None.

        """
        #updating the exogenous variables to current state
        self.pop_rur = exogenous["pop_rur"]
        self.pop_urb = exogenous["pop_urb"]

        self.rain = exogenous["rain"]
        self.cer_imp = exogenous["net_imp"]
        self.liv = exogenous["liv"]
        self.crop_yield = exogenous["yield"]

        if "biom_prod" in exogenous:
            self.biom_prod = exogenous["biom_prod"]
        else:
            self.biom_prod = self.b_biom_prod + self.a_biom_prod*self.rain
            #biomass productivity per year, [biom_prod]=tonnes/ha

        #calculation
        self.veg_d = (self.pop_rur*self.fuel_conso_rur +\
                      self.pop_urb*self.fuel_conso_urb)/self.veg_prod

        self.crop_subs = self.pop_rur*self.food_conso/self.crop_yield
        self.crop_mark = (self.pop_urb*self.food_conso - self.cer_imp)/self.crop_yield

        self.fal_d = self.cf_init*(self.crop_subs + self.crop_mark)
        self.crop_d = self.crop_subs + self.crop_mark + self.fal_d
        self.past_d = [(self.liv*self.biom_conso_min)/self.biom_prod,
                       (self.liv*self.biom_conso_max)/self.biom_prod]

        self.land_d = self.crop_d - self.prev_crop + self.past_d[1] - self.prev_past
        self.land_d_no_fal = (self.crop_subs + self.crop_mark) -\
            (self.prev_crop_subs + self.prev_crop_mark) +\
                self.past_d[0] - self.prev_past



    def calculate_land_use(self, exogenous, calculate_demand):
        """
        Calculates land use, that is to say the
        quantity of land dedicated to each use
        (fuelwood extraction, cropland...).

        Parameters
        ----------
        exogenous : pd.DataFrame row 
            contains the value of the exogenous
            variables for the year considered.

        Returns
        -------
        None.

        """
        #calculating demand
        self.calculate_demand(exogenous)

        if calculate_demand:
            #we only calculate the demand for pastoral lands, market and subsistence croplands
            self.prev_fal = 0
            self.prev_past = self.liv*self.biom_conso_min/self.biom_prod
            self.prev_veg = self.veg_d
            self.prev_un = 0
            self.prev_crop_subs = self.crop_subs
            self.prev_crop_mark = self.crop_mark

        else:
            #calculating land use
            if self.prev_veg + self.prev_un - self.land_d > self.veg_d :
                #there is enough space for everything : expansion phase
                self.intensification = 0
                if self.prev_un - self.land_d < 0 :
                    #there is a need for deforestation
                    self.prev_veg -= self.land_d - self.prev_un
                self.prev_crop = self.crop_d
                self.prev_past = self.past_d[1] #we use the highest biomass consomation
                self.prev_fal = self.fal_d
                if calculate_demand:
                    self.prev_fal=0
    
            else :
                #there are conflicts in land use : intensification phase
                self.intensification = 1
                #min_past = self.liv*self.biom_conso_min/self.biom_prod
                #the minimal amount of land necessary for pasture


    
                #using delta fal
                self.prev_fal += ((self.crop_subs + self.crop_mark) -\
                                          (self.prev_crop_subs + self.prev_crop_mark))*self.cf_init -\
                                        (self.fal_d - self.prev_fal + self.land_d_no_fal-self.prev_un)*\
                                            (1-self.crop_past_ratio)
                self.prev_fal = min((self.crop_subs + self.crop_mark)*self.cf_init,
                                    self.prev_fal)
                #fal can't be bigger than cf_init * (crop_mark + crop_subs)
                self.prev_fal = max(self.prev_fal,
                                    0)
                #fal can't be negative
                if self.prev_fal<self.cf_inf *(self.crop_subs +self.crop_mark):
                    #treshold on fal, default threshold is 0
                    self.prev_fal = self.cf_inf *(self.crop_subs + self.crop_mark)
                prev_veg = min(self.veg_d,
                               self.prev_veg)
                self.prev_past = max(self.area - prev_veg - self.prev_fal -\
                                         self.crop_subs - self.crop_mark,
                                         0)
                if self.prev_past > (self.liv*self.biom_conso_max)/self.biom_prod:
                    rest = self.prev_past - (self.liv*self.biom_conso_max)/self.biom_prod
                    self.prev_veg = min(self.prev_veg,
                                        self.veg_d + rest)
                    self.prev_past = (self.liv*self.biom_conso_max)/self.biom_prod
            self.prev_crop_subs = self.crop_subs # demand
            self.prev_crop_mark = self.crop_mark
            self.prev_crop = self.prev_crop_subs + self.prev_crop_mark + self.prev_fal

            #having calculated all land uses, the only thing left is unused land
            self.prev_un = max(self.area - self.prev_past - self.prev_veg - self.prev_crop,
                               0)
            #un can only take positive values