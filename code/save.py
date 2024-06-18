# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 16:07:36 2024

@author: anem
This file contains functions to save and load 
the data obtained from sampling not to have to
do calculations multiple times.
"""

#imports
from datetime import date
from os.path import exists
import pandas as pd
import openpyxl


#functions
def save_sampling(msd_list, params_list, path_results):
    """
    Creates an xlsx file containing the parameter values
    and associated MSDs.

    Parameters
    ----------
    msd_list : list of MSD values
            obtained by comparing the output 
            of the model for parameter values 
            at the same index in params_list
            and FAO land use data.
    params_list : list containg dictionaries 
            of parameter values sampled for
            parameter optimization.
    path_results : str path where we want to
            save msd and parameter values.

    Returns
    -------
    path_2results : STR PATH OF FILE IN WHICH
            MSD_LIST AND PARAMS_LIST WILL BE
            SAVED.

    """
    cur_date = str(date.today()) #fetch current date
    
    #determining name
    i=1
    while exists(path_results + f'{cur_date}params_random_search_0{i}.xlsx'):
        i+=1
    path_2results = path_results + f'{cur_date}params_random_search_0{i}.xlsx'
    
    #saving results
    df = pd.DataFrame.from_dict(params_list)
    df.to_excel(path_2results)
    
    #adding msd values
    column = len(params_list[0].keys())+2 #at which column to put msd values
    workbook = openpyxl.load_workbook(path_2results)
    worksheet = workbook.worksheets[0]
    cell_title = worksheet.cell(row=1, column=column)
    cell_title.value = 'MSD'
    y=2
    for x in range(len(msd_list)):
        cell_to_write = worksheet.cell(row=y, column=column)
        cell_to_write.value = msd_list[x]
        y += 1
    workbook.save(path_2results)
    
    return path_2results