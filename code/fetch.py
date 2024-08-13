# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 20:20:04 2024

@author: anem
"""

import pandas as pd

def df(path):
    inputs_df = pd.read_excel(path)
    return inputs_df