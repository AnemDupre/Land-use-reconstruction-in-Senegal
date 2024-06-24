# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 10:56:31 2024

@author: anem
"""

path_gridded = "C:\\Users\\emili\\OneDrive\\Documents\\academique\\M2_ens_ulm\\S2_stage\\repository_updated\\data\\Senegal\\inputs\\cattle_gridded_2015"
import os 
os.chdir(path_gridded)

from PIL import Image
import numpy as np

im = Image.open("5_Ct_2015_Da.tif")
im.show()

imarray = np.array(im)
imarray.shape
