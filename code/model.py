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
    def __init__(self, NAT_AREA, exogenous_df, preservation=True, params=None):
        #initializing the land use calculator with NAT_AREA and data from the frst year
        self.land_use_calculator = LandUseCalculator(NAT_AREA, exogenous_df.iloc[0], params=params)
        self.exogenous_df = exogenous_df
        self.preservation = preservation #if fuelwood extraction areas are protected
        
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
            self.land_use_calculator.calculate_land_use(row, self.preservation)
            
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
    def __init__(self, NAT_AREA, exogenous, params=None):

        #initializing parameters
        self.NAT_AREA = NAT_AREA #national area [NAT_AREA]=ha

        if params!=None:
            self.BIOM_CONSO_MIN = params["biom_conso_min"]
            self.BIOM_CONSO_MAX = params["biom_conso_max"]
            self.FOOD_CONSO = params["food_conso"]
            self.CF_INIT = params["cf"]
            self.CF = params["cf"]
            self.FUEL_CONSO_RUR = params["fuel_conso_rur"]
            self.FUEL_CONSO_URB = params["fuel_conso_urb"]
            self.VEG_PROD = params["veg_prod"]
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
            self.BIOM_CONSO_MIN = 2.3 #minimal biomass consumption during intensification
            self.BIOM_CONSO_MAX = 4.6 #biomass consumption during expansion
            self.FOOD_CONSO = 360 #food consumption [FOOD_CONSO]=kg/inhab
            self.CF_INIT = 2
            self.CF = 2 #cultivation frequency (dimensionless)
            self.FUEL_CONSO_RUR = 0.65 #rural fuel consumption [FUEL_CONSO_RUR]=m3/inhab
            self.FUEL_CONSO_URB = 0.83 #urban fuel consumption [FUEL_CONSO_URB]=m3/inhab
            self.VEG_PROD = 0.75 #productivity in fuelwood [VEG_PROD]=m3/ha
            self.a_biom_prod = 0.00375
            self.b_biom_prod = 0.15
            self.crop_past_ratio = 2/3
        
        self.CC = 1.25 #carrying capacity of pastural land [CC]=ha/TLU
        self.BIOM_CONSO = [self.BIOM_CONSO_MIN,
                           self.BIOM_CONSO_MAX]
        #consumption in biomass per head [BIOM_CONSO]=tonnes/equivalent TLU
        
        #Initial exogeneous variables 
        self.pop_rur = exogenous["pop_rur"] #rural population in inhab
        self.pop_urb = exogenous["pop_urb"] #urban population in inhab
        self.rain = exogenous["rain"] #yearly precipitation in mm
        self.cer_imp = exogenous["net_imp"] #cereal imports in kg
        self.liv = exogenous["liv"] #livestock population in equivalent TLU
        self.crop_yield = exogenous["yield"] #crop yield [crop_yield]=kg/ha
        if "biom_prod" in exogenous:
            self.biom_prod = exogenous["biom_prod"]
        else:
            self.biom_prod = self.b_biom_prod +self.a_biom_prod*self.rain #biomass productivity per year [biom_prod]=tonnes/ha  
        
        #initializing land demand  (we only need to calculate crop_d and past_d for initialization)
        self.veg_d = 0 #demand for land destined to fuelwood extraction in ha
        self.crop_subs = self.pop_rur*self.FOOD_CONSO/self.crop_yield #demand for cropland for subsistence agriculture in ha
        self.crop_mark = (self.pop_urb*self.FOOD_CONSO - self.cer_imp)/self.crop_yield #demand for cropland for commercial agriculture in ha
        self.fal_d = self.CF*(self.crop_subs + self.crop_mark) #demand for land destined to fallow in ha
        self.crop_d = self.crop_subs + self.crop_mark + self.fal_d #total demand of cropland in ha
        self.past_d = self.liv*self.BIOM_CONSO[1]/self.biom_prod #pastoral land demand in ha
        
        #land use of previous state
        self.prev_un = 0 #unused area in ha
        if self.NAT_AREA - self.prev_un - self.past_d - self.crop_d > 0:
            self.prev_veg = self.NAT_AREA - self.prev_un - self.past_d - self.crop_d #land covered by natural vegetation (ha)
            self.prev_past = self.past_d #pastoral land (ha)
            self.prev_crop = self.crop_d #cropland (ha)
        
        else :# we are already in an intensification state
            self.prev_veg = self.NAT_AREA
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
            self.biom_prod = self.b_biom_prod + self.a_biom_prod*self.rain #biomass productivity per year [biom_prod]=tonnes/ha    
        
        #calculation
        self.veg_d = (self.pop_rur*self.FUEL_CONSO_RUR + self.pop_urb*self.FUEL_CONSO_URB)/self.VEG_PROD

        self.crop_subs = self.pop_rur*self.FOOD_CONSO/self.crop_yield
        self.crop_mark = (self.pop_urb*self.FOOD_CONSO - self.cer_imp)/self.crop_yield
        
        self.fal_d = self.CF*(self.crop_subs + self.crop_mark)
        self.crop_d = self.crop_subs + self.crop_mark + self.fal_d
        self.past_d = [(self.liv*self.BIOM_CONSO[0])/self.biom_prod, (self.liv*self.BIOM_CONSO[1])/self.biom_prod]
    
        self.land_d = self.crop_d - self.prev_crop + self.past_d[1] - self.prev_past
        self.land_d_no_fal = (self.crop_subs + self.crop_mark) - (self.prev_crop_subs + self.prev_crop_mark) + self.past_d[1] - self.prev_past
        
        
        
    def calculate_land_use(self, exogenous, preservation):
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
            
        else :
            #there are conflicts in land use : intensification phase
            self.intensification = 1
            if preservation==True:
                self.prev_veg = min(self.veg_d, self.prev_veg)

                #using delta fal
                max_past = self.liv*self.BIOM_CONSO_MAX/self.biom_prod
                
                #self.prev_fal = (self.crop_subs +self.crop_mark)*self.CF_INIT - ((self.crop_subs +self.crop_mark)*self.CF_INIT - self.prev_fal + self.land_d_no_fal-self.prev_un)*(1-self.crop_past_ratio)
                self.prev_fal += ((self.crop_subs + self.crop_mark) - (self.prev_crop_subs + self.prev_crop_mark))*self.CF_INIT - (self.fal_d - self.prev_fal + self.land_d_no_fal-self.prev_un)*(1-self.crop_past_ratio)
                self.prev_fal = max(self.prev_fal, self.NAT_AREA - self.prev_veg - self.crop_subs - self.crop_mark - max_past, 0) #fal can't be negative
                self.prev_fal = min((self.crop_subs +self.crop_mark)*self.CF_INIT, self.prev_fal) #fal can't be bigger than CF_init * (crop_mark + crop_subs)
                
                #treshold on fal
                if self.prev_fal<self.cf_inf *(self.crop_subs +self.crop_mark):
                    self.prev_fal = self.cf_inf *(self.crop_subs + self.crop_mark)
                #print(self.prev_fal)
                self.prev_past = max(min(self.NAT_AREA - self.prev_veg - self.prev_fal - self.prev_crop_subs - self.prev_crop_mark, self.liv*self.BIOM_CONSO_MAX/self.biom_prod), 0)
                
                
            else: #fuelwood extraction areas are not protected 

                #using delta fal
                max_past = self.liv*self.BIOM_CONSO_MAX/self.biom_prod
                
                #self.prev_fal = (self.crop_subs +self.crop_mark)*self.CF_INIT - ((self.crop_subs +self.crop_mark)*self.CF_INIT - self.prev_fal + self.land_d_no_fal-self.prev_un)*(1-self.crop_past_ratio)
                self.prev_fal += ((self.crop_subs + self.crop_mark) - (self.prev_crop_subs + self.prev_crop_mark))*self.CF_INIT - (self.fal_d - self.prev_fal + self.land_d_no_fal-self.prev_un)*(1-self.crop_past_ratio)
                self.prev_fal = max(self.prev_fal, self.NAT_AREA - self.crop_subs - self.crop_mark - max_past, 0) #fal can't be negative
                self.prev_fal = min((self.crop_subs +self.crop_mark)*self.CF_INIT, self.prev_fal) #fal can't be bigger than CF_init * (crop_mark + crop_subs)
                
                #treshold on fal
                if self.prev_fal<self.cf_inf *(self.crop_subs +self.crop_mark):
                    self.prev_fal = self.cf_inf *(self.crop_subs + self.crop_mark)
                #print(self.prev_fal)
                self.prev_past = max(min(self.NAT_AREA - self.prev_fal - self.prev_crop_subs - self.prev_crop_mark, self.liv*self.BIOM_CONSO_MAX/self.biom_prod), 0)
                self.prev_veg = max(0, self.NAT_AREA - self.prev_fal - self.prev_crop_subs - self.prev_crop_mark - self.prev_past)
                
        self.prev_crop_subs = self.crop_subs # demand
        self.prev_crop_mark = self.crop_mark

        #having calculated all land uses, the only thing left is unused land
        self.prev_un = max(self.NAT_AREA - self.prev_past - self.prev_veg - self.prev_crop, 0) #we only want positive values for un
        
        if self.prev_crop_subs + self.prev_crop_mark + self.prev_past + self.prev_fal + self.prev_veg > self.NAT_AREA:
            sum_land_d = self.prev_crop_subs + self.prev_crop_mark + self.prev_past + self.prev_fal
            #we normalize the values
            self.prev_crop_subs = (self.NAT_AREA-self.prev_veg) * self.prev_crop_subs / sum_land_d
            self.prev_crop_mark = (self.NAT_AREA-self.prev_veg) * self.prev_crop_mark / sum_land_d
            self.prev_past = (self.NAT_AREA-self.prev_veg) * self.prev_past / sum_land_d
            self.prev_fal = (self.NAT_AREA-self.prev_veg) * self.prev_fal / sum_land_d
        
        self.prev_crop = self.prev_crop_subs + self.prev_crop_mark + self.prev_fal
        