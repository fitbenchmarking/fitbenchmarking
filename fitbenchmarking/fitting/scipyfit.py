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
        chisq(status, fit_wks, min_chi_sq, best_fit, minimizer)
        individual_result = \
        misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                 function, fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit

def fit(problem, data, function, minimizer, cost_function):

    popt, pcov, t_start, t_end = None, None, None, None
    try:
        t_start = time.clock()
        if cost_function == 'least squares':
            popt, pcov = curve_fit(f=function, xdata=data[0], ydata=data[1],
                                   sigma=data[2], p0=initial_params)
        elif cost_function == 'unweighted least squares':
            popt, pcov == curve_fit(f=function, xdata=data[0], ydata=data[1],
                                    p0=initial_params, )
        t_end = time.clock()
    except(RuntimeError, ValueError) as err:
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

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

    function_defs = []
    if problem.type == 'nist':
        return nist_func_definitions(problem.equation, problem.starting_values)
    elif problem.type == 'neutron':
        function_defs.append(neutron_func_definition(problem.equation))
        return function_defs
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
        function_parameters.append('A0=0,A1=0,')

    function_parameters[-1] = function_parameters[-1].replace(',', ', ')
    return function_names, function_parameters

def make_neutron_fit_function(func_name, fit_function):

    func_obj = parse_neutron.gen_func_obj(func_name)
    if fit_function == None: fit_function = func_obj
    else: fit_function += func_obj

    return fit_function

def make_neutron_initial_parameters(function_params):


def neutron_func_definition(functions_string):

    functions = functions_string.split(';')
    function_names, function_params = [], []
    for function in functions:
        function_names, function_params = \
        get_neutron_func(function, function_names, function_params)

    for name in function_names:
        fit_function = make_neutron_fit_function(name, fit_function)

    make_neutron_initial_parameters()

    return fit_function
