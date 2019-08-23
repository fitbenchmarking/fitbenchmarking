"""
Benchmark fitting functions for the scipy software.
"""
# Copyright &copy; 2016 ISIS Rutherford Appleton Laboratory, NScD
# Oak Ridge National Laboratory & European Spallation Source
#
# This file is part of Mantid.
# Mantid is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Mantid is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# File change history is stored at:
# <https://github.com/mantidproject/fitbenchmarking>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>
from __future__ import (absolute_import, division, print_function)

from scipy.optimize import curve_fit
import numpy as np
import sys
import time
import re

from fitting import misc
from sasmodels.bumps_model import Experiment, Model
from bumps.names import *
from bumps.fitters import fit as bumpsFit
from fitting.sasview.func_def import get_init_function_def, get_fin_function_def
from fitting.plotting import plot_helper
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max


def benchmark(problem, data, function, minimizers, cost_function):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the SasView fitting software.

    @param problem :: a problem object containing information used in fitting
    @param data :: object holding the problem data
    @param function :: the fitted function (model for SasView problems)
    @param minimizers :: array of minimizers used in fitting
    @param cost_function :: the cost function used for fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit
    """
    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []

    for minimizer in minimizers:

        init_func_def = get_init_function_def(function, problem)
        status, fitted_y, fin_func_def, runtime = \
            fit(problem, data, function, minimizer, init_func_def)
        chi_sq, min_chi_sq, best_fit = \
            chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer)

        individual_result = \
                misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                     init_func_def, fin_func_def)

        results_problem.append(individual_result)

    return results_problem, best_fit

def fit(problem, data, function, minimizer, init_func_def):
    """

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
        if isinstance(problem.starting_values, basestring):
            function_without_ties = re.sub(r",(\s+)?ties=[(][A-Za-z0-9=.,\s+]+[)]", '', problem.equation)
            function_list = (function_without_ties).split(';')
            func_params_list = [(func.split(','))[1:] for func in function_list]
            formatted_param_list = ['f'+str(func_params_list.index(func_params))+'.'+param.strip() for func_params in func_params_list for param in func_params]
            param_names = [(param.split('='))[0] for param in formatted_param_list if not 'BinWidth' in param]
            formatted_param_names = [param.replace('.', '_') for param in param_names]
        else:
            formatted_param_names = [param[0] for param in problem.starting_values]

        param_values = function[1]
        param_string = ''
        for name, value in zip(formatted_param_names, param_values):
            if not name.endswith('BinWidth'):
                param_string += "," + name + "=" + str(value)

        exec ('func_wrapper = Curve(model, x=data.x, y=data.y, dy=data.dy' + param_string + ')')

        for name, value in zip(formatted_param_names, param_values):
            minVal = -np.inf
            maxVal = np.inf
            if not name.endswith('BinWidth'):
                exec ('func_wrapper.' + name + '.range(' + str(minVal) + ',' + str(maxVal) + ')')
    else:
        exec ("params = dict(" + problem.starting_values + ")") in locals()

        model_wrapper = Model(model, **params)
        for range in problem.starting_value_ranges.split(';'):
            exec ('model_wrapper.' + range)
        func_wrapper = Experiment(data=data, model=model_wrapper)

    fitProblem = FitProblem(func_wrapper)

    try:
        t_start = time.clock()
        result = bumpsFit(fitProblem, method=minimizer)
        t_end = time.clock()
    except (RuntimeError, ValueError) as err:
        logger.warning("Fit failed: " + str(err))

    status = 'success' if result.success is True else 'failed'

    fitted_y = func_wrapper.theory()

    final_param_values = result.x

    fin_func_def = get_fin_function_def(final_param_values, problem, init_func_def)

    runtime = t_end - t_start

    return status, fitted_y, fin_func_def, runtime

def chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer_name):
    """
    Calculates the chi squared and compares it to the minimum chi squared
    found until now. If the current chi_squared is lower than the minimum,
    the new values becomes the minimum and the data of the fit is stored
    in the variable best_fit.

    @param status :: the status of the fit, either success or failure
    @param fitted_y :: the y-data of the fit
    @param min_chi_sq :: the minimum chi_squared value
    @param best_fit :: object where the best fit data is stored
    @param minimizer_name :: name of the minimizer used in storing the
                             best_fit data

    @returns :: The chi-squared values, the minimum chi-squared found
                until now and the best fit data object
    """
    if status != 'failed':
        differences = fitted_y - data.y
        chi_sq = misc.compute_chisq(differences)
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = plot_helper.data(minimizer_name, data.x, fitted_y)
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan

    return chi_sq, min_chi_sq, best_fit
