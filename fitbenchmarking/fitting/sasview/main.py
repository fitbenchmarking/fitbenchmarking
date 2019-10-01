"""
Benchmark fitting functions for the scipy software.
"""

from __future__ import (absolute_import, division, print_function)

from scipy.optimize import curve_fit
import numpy as np
import sys
import time
import re

from fitbenchmarking.fitting import misc
from sasmodels.bumps_model import Experiment, Model
from bumps.names import *
from bumps.fitters import fit as bumpsFit
from fitbenchmarking.fitting.sasview.func_def import (
    get_init_function_def, get_fin_function_def
)
from fitbenchmarking.fitting.plotting import plot_helper
from fitbenchmarking.utils.logging_setup import logger


def fit(problem, data, function, minimizer, init_func_def):
    """
    The SasView fit software. The fitting process is done by Bumps fitting.

    @param problem :: a problem object containing information used in fitting
    @param model :: the fitted function (model for SasView problems)
    @param minimizer :: the minimizer used in the fitting
    @param init_func_def :: the initial function definition

    @returns ::  the status, either success or failure (str), the data
                of the fit, the final function definition and the
                runtime of the fitting software
    """

    t_start, t_end = None, None
    model = function[0]

    if hasattr(model, '__call__'):
        #The function is not native to SasView
        if isinstance(problem.starting_values, basestring):
            #The problem type is FitBenchmark
            #Remove ties from the expresstion
            function_without_ties = re.sub(r",(\s+)?ties=[(][A-Za-z0-9=.,\s+]+[)]", '', problem.equation)

            #Formatting the function parameter names
            function_list = (function_without_ties).split(';')
            func_params_list = [(func.split(','))[1:] for func in function_list]
            formatted_param_list = ['f'+str(func_params_list.index(func_params))+'.'+param.strip() for func_params in func_params_list for param in func_params]
            param_names = [(param.split('='))[0] for param in formatted_param_list if not 'BinWidth' in param]
            formatted_param_names = [param.replace('.', '_') for param in param_names]
        else:
            # The problem type is NIST
            #Formatting the function parameter names
            formatted_param_names = [param[0] for param in problem.starting_values]

        param_values = function[1]

        #Remove any function attribute. BinWidth is the only attribute in all FitBenchmark (Mantid) problems.
        param_string = ''
        for name, value in zip(formatted_param_names, param_values):
            if not name.endswith('BinWidth'):
                param_string += "," + name + "=" + str(value)

        #Create a Function Wrapper for the problem function. The type of the Function Wrapper is acceptable by Bumps.
        exec ('func_wrapper = Curve(model, x=data.x, y=data.y, dy=data.dy' + param_string + ')')

        #Set a range for each parameter
        for name, value in zip(formatted_param_names, param_values):
            minVal = -np.inf
            maxVal = np.inf
            if not name.endswith('BinWidth'):
                exec ('func_wrapper.' + name + '.range(' + str(minVal) + ',' + str(maxVal) + ')')
    else:
        # The function is native to SasView
        exec ("params = dict(" + problem.starting_values + ")") in locals()

        #Create the Model wrapper for SasView models
        model_wrapper = Model(model, **params)

        # Set a range for each parameter
        for range in problem.starting_value_ranges.split(';'):
            exec ('model_wrapper.' + range)

        # Create a Function Wrapper for the problem function. The type of the Function Wrapper is acceptable by Bumps.
        func_wrapper = Experiment(data=data, model=model_wrapper)

    #Create a Problem Wrapper. The type of the Problem Wrapper is acceptable by Bumps fitting.
    fitProblem = FitProblem(func_wrapper)

    #Fitting using Bumps
    try:
        t_start = time.clock()
        result = bumpsFit(fitProblem, method=minimizer)
        t_end = time.clock()
    except (RuntimeError, ValueError) as err:
        logger.warning("Fit failed: " + str(err))

    #Get fitting status
    status = 'success' if result.success is True else 'failed'

    #Evaluate the function/model for the fitted Y values
    fitted_y = func_wrapper.theory()

    #Final paramter values
    final_param_values = result.x

    #Final function definition string
    fin_func_def = get_fin_function_def(final_param_values, problem, init_func_def)

    #Runtime of the fit
    runtime = t_end - t_start

    return status, fitted_y, fin_func_def, runtime
