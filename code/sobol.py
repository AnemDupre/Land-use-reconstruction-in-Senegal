# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 09:30:31 2024

@author: anem
"""

from SALib.sample import saltelli
from SALib.analyze import sobol
import numpy as np
import scipy
import model
import fetch



def run_model_w_params(params_sample, area, inputs):
    """
    Runs the model for the given parameter sample and returns the area
    under the curve of outputs "past", "crop_subs", "crop_mark", "fal",
    "un", and "veg".

    Parameters
    ----------
    params_sample : DIC
        Parametrization.
    area : INT or FLOAT
        Surface of the considered region.
    inputs : DATAFRAME
        Time series used as inputs.

    Returns
    -------
    integ : ARRAY
        For each considered output, the area under the curve.

    """

    output_items = ["past", "crop_subs", "crop_mark", "fal", "un", "veg"]

    #initializing the params dictionary
    params = {"biom_conso_min" : 0, #minimal biomass consumption during intensification
              "biom_conso_max" : 0, #biomass consumption during expansion
              "food_conso" : 0, #food consumption [FOOD_CONSO]=kg/inhab
              "cf" : 0, #cultivation frequency (dimensionless)
              "fuel_conso_rur" : 0, #rural fuel consumption [FUEL_CONSO_RUR]=m3/inhab
              "fuel_conso_urb" : 0, #urban fuel consumption [FUEL_CONSO_URB]=m3/inhab
              "veg_prod" : 0, #productivity in fuelwood [VEG_PROD]=m3/ha
              "a_biom_prod" : 0,
              "b_biom_prod" : 0}

    #let's give to each parameter its value according to params_sample
    keys = list(params.keys())
    for i, key in enumerate(keys):
        params[key] = params_sample[i]

    #run the model
    lu_model = model.LandUseModel(area, inputs, params=params)
    lu_model.iterate()

    #extract outputs and calculate the integrals
    outputs = lu_model.lu_memory
    outputs = outputs[output_items]
    integ = np.zeros(6)
    for i in range(6):
        item = output_items[i]
        output = outputs[item].to_numpy()
        integ[i] = scipy.integrate.trapz(output, x=None, dx=1.0)
        #we only keep the area under the curve for each output
    return integ



def test_param_sensitivity(area, inputs, numb_samples):
    """
    Calculates Sobol indices for the parameters of the model.

    Parameters
    ----------
    area : INT or FLOAT
        Surface of the considered region.
    inputs : DATAFRAME
        Time series used as inputs.
    numb_samples : INT
        Number of parameter samples generated to calculate Sobol indices.

    Returns
    -------
    None.

    """
    #get parameter ranges
    params = fetch.parameter_ranges()

    #define parameter ranges
    problem = {
        'num_vars': 10,  # Number of parameters
        'names': list(params.keys()),  # Parameter names
        'bounds': list(params.values())  # Parameter ranges
    }

    #generate parameter samples
    param_samples = saltelli.sample(problem, numb_samples,
                                    calc_second_order=False)
    #generates a matrix with numb_samples * (num_vars + 2) rows
    #the number of samples must allow for convergence of Sobol indices

    #calculate model outputs for each parameter set sampled
    model_outputs = run_model_w_params(param_samples[0], area, inputs)
    for params_sample in param_samples[1:] :
        output = run_model_w_params(params_sample, area, inputs)
        model_outputs = np.hstack([model_outputs, output])
        #concatenate results

    #perform sensitivity analysis using Sobol method
    sobol.analyze(problem, model_outputs,
                  calc_second_order=False,
                  print_to_console=True)
