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

from fitting import misc
from fitting.scipy.func_def import get_init_function_def
from fitting.scipy.func_def import get_fin_function_def
from fitting.plotting import plot_helper
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max


def benchmark(problem, data, function, minimizers, cost_function):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the scipy fitting software.

    @param problem :: a problem object containing information used in fitting
    @param data :: workspace holding the problem data
    @param function :: the fitted function
    @param minimizers :: array of minimizers used in fitting
    @param cost_function :: the cost function used for fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit
    """
    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []

    for minimizer in minimizers:
        init_function_def = get_init_function_def(function, problem.equation)
        status, fitted_y, fin_function_def, runtime = \
            fit(data, function, minimizer, cost_function, init_function_def)
        chi_sq, min_chi_sq, best_fit = \
            chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer)
        individual_result = \
            misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                     init_function_def, fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit


def fit(data, function, minimizer, cost_function, init_function_def):
    """
    Perform a fit for a single minimizer using the scipy fitting
    software

    @param data :: workspace holding the problem data
    @param function :: the fitted function
    @param minimizer :: the minimizer used in the fitting process
    @param cost_function :: the type of cost function used in fitting
    @param init_function_def :: string containing the initial function
                                definition

    @returns :: the status, either success or failure (str), the data
                of the fit, the final function definition and the
                runtime of the fitting software
    """
    popt, t_start, t_end = None, None, None
    func_callable = function[0]
    initial_params = function[1]

    try:
        t_start = time.clock()
        popt = execute_fit(func_callable, data, initial_params,
                           minimizer, cost_function)
        t_end = time.clock()
    except(RuntimeError, ValueError) as err:
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

    fin_def = None
    if not popt is None:
        fin_def = get_fin_function_def(init_function_def, func_callable, popt)
    status, fitted_y, runtime = \
        parse_result(func_callable, popt, t_start, t_end, data[0])

    return status, fitted_y, fin_def, runtime


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
        differences = fitted_y - data[1]
        chi_sq = misc.compute_chisq(differences)
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = plot_helper.data(minimizer_name, data[0], fitted_y)
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan

    return chi_sq, min_chi_sq, best_fit


def execute_fit(function, data, initial_params, minimizer, cost_function):
    """
    Helper function that executes the fit depending on the type
    of cost_function the user wants.

    @param initial_params :: array of initial parameters given
                             to the variables defining the function

    @returns :: array of final variables after the fit was performed
    """
    popt, pcov = None, None
    if cost_function == 'least squares':
        popt, pcov = curve_fit(f=function.__call__,
                               xdata=data[0], ydata=data[1], p0=initial_params,
                               sigma=data[2], method=minimizer, maxfev=500)
    elif cost_function == 'unweighted least squares':
        popt, pcov = curve_fit(f=function.__call__,
                               xdata=data[0], ydata=data[1],
                               p0=initial_params, method=minimizer, maxfev=500)
    return popt


def parse_result(function, popt, t_start, t_end, data_x):
    """
    Helper function that parses the result and processes it into
    a useful form. Returns the status, fitted y data and runtime of the fit.
    """
    status = 'failed'
    fitted_y, runtime = None, np.nan
    if not popt is None:
        status = 'success'
        fitted_y = get_fittedy(function, data_x, popt)
        runtime = t_end - t_start

    return status, fitted_y, runtime


def get_fittedy(function, data_x, popt):
    """
    Gets the fitted y data corresponding to given x values.
    """
    try:
        fitted_y = function.__call__(data_x)
    except:
        fitted_y = function(data_x, *popt)

    return fitted_y
