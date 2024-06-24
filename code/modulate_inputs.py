# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:30:46 2024

@author: anem
"""


def change_amplitude(inputs, columns, amplitude):
    
    modified_inputs = inputs.copy()
    for column in columns :
        modified_inputs[column] = modified_inputs[column].apply(lambda x: x*amplitude)
    
    return modified_inputs

