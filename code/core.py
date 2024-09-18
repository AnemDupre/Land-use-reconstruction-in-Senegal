# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:17:41 2024

@author: anem
"""

from functools import reduce
import pandas as pd



def merge_df(df_list, column="Year"):
    merged_df = reduce(lambda  left,right: pd.merge(left,right,on=[column], how='left'), df_list)
    return merged_df

def remove_values_under_thres(the_list, val):
   return [value for value in the_list if value >= val]
