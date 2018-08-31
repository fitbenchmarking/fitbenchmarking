"""
Fittng and utility functions for the scipy fitting algorithms.
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
import re
import copy

from fitting import misc
from parsing import parse_neutron
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max

def benchmark(problem, data, function, minimizers, cost_function):

    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []

    for minimizer in minimizers:
        status, fin_function_def, runtime = \
        fit(problem, data, function, minimizer, cost_function)
        chi_sq, min_chi_sq, best_fit = \
        chisq()
        individual_result = \
        misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                 function, fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit

def fit(problem, data, function, minimizer, cost_function):

    popt, pcov, t_start, t_end = None, None, None, None
    initial_params = function[1]
    func_callable = function[0]

    try:
        t_start = time.clock()
        popt = execute_fit(func_callable, data, initial_params, minimizer,
                           cost_function)
        t_end = time.clock()
    except(RuntimeError, ValueError) as err:
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

    status, fin_function_def, runtime = \
    parse_result(func_callable, popt, t_start, t_end, problem)

    return status, differences, fin_function_def, runtime

def execute_fit(function, data, initial_params, minimizer, cost_function):

    if cost_function == 'least squares':
        popt, pcov = curve_fit(f=function.__call__, xdata=data[0],
                               ydata=data[1], sigma=data[2], p0=initial_params,
                               method=minimizer)
    elif cost_function == 'unweighted least squares':
        popt, pcov = curve_fit(f=function.__call__, xdata=data[0],
                               ydata=data[1], p0=initial_params,
                               method=minimizer)
    return popt

def parse_result(function, popt, t_start, t_end, problem):

    status = 'failed'
    fin_function_def, differences, runtime = None, None, np.nan
    if not popt is None:
        status = 'success'
        function = create_final_function_callable()
        differences = calculate_differences(popt, problem, function)
        fin_function_def = create_final_function_def(problem, popt)
        runtime = t_end - t_start

    return status, differences, fin_function_def, runtime

def calculate_differences(popt, problem, function):

    measured_y = copy.copy(problem.data_y)
    fitted_y = function(copy.copy(problem.data_x))





def create_final_function_def(problem, popt):

    fin_function_def = problem.equation

    find_float = re.compile("[-+]?[0-9]*\.?[0-9]+")
    for idx in range(len(popt)):
        fin_function_def = find_float.sub(popt[idx], fin_function_def,  idx)

    return fin_function_def

def prepare_data(problem, use_errors):

    if use_errors:
        data = np.array(np.copy(problem.data_x), np.copy(problem.data_y),
                        np.copy(problem.data_e))
        cost_function = 'least squares'
    else:
        data = np.array(np.copy(problem.data_x), np.copy(problem.data_y))
        cost_function = 'unweighted least squares'

    return data, cost_function

def function_definitions(problem):

    if problem.type == 'nist':
        return nist_func_definitions(problem.equation, problem.starting_values)
    elif problem.type == 'neutron':
        return neutron_func_definitions(problem.equation)
    else:
        RuntimeError("Your desired algorithm is not supported yet!")

def nist_func_definitions(function, startvals):

    startvals = np.array(startvals, dtype=object)
    params = ", ".join(param for param in startvals[:, 0])

    function = function.replace("exp", "np.exp")

    function_defs = []
    for values in starting_values[:, 1]:
        exec "def fitting_function(x, " + params + "): return " + function
        function_defs.append([fitting_function, values])

    return function_defs

def get_neutron_func(function, function_names, function_parameters):

    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
        function_parameters.append(function[first_comma+1:])
    else:
        function_names.append(function[5:])
        function_parameters.append('')

    function_parameters[-1] = function_parameters[-1].replace(',', ', ')
    return function_names, function_parameters

def make_neutron_fit_function(func_name, fit_function):

    func_obj = parse_neutron.gen_func_obj(func_name)
    if fit_function == None: fit_function = func_obj
    else: fit_function += func_obj

    return fit_function

def find_neutron_params(param_set, params):

    while True:
        comma = param_set.find(',', start)
        if comma == -1: break;
        equal = param_set.find('=', start)
        parameter = param_set[equal+1:comma-1]
        params.append(parameter)
        start = comma + 1

    return params

def get_neutron_initial_parameters(function_params):

    params = []
    for param_set in function_params:
        start = 0
        find_neutron_params(param_set, params)

    return params

def neutron_func_definitions(functions_string):

    function_defs = []
    functions = functions_string.split(';')
    function_names, function_params = [], []
    for function in functions:
        function_names, function_params = \
        get_neutron_func(function, function_names, function_params)
    for name in function_names:
        fit_function = make_neutron_fit_function(name, fit_function)

    params = make_neutron_initial_parameters(function_params)
    function_defs = [[fit_function, params]]

    return function_defs

def chisq(status, fit_wks, min_chi_sq, best_fit, minimizer):

    if status != 'failed':
        chi_sq = misc.compute_chisq(fit_wks.readY(2))
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = optimum(fit_wks, minimizer, best_fit)
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan

    return chi_sq, min_chi_sq, best_fit
