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
import sys, re, copy, time

from fitting import misc
from fitting import mantid
from fitting.plotting import plot_helper
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max

def benchmark(problem, data, function, minimizers, cost_function):

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

    fin_func_def = None
    if not popt is None:
        fin_func_def = get_fin_function_def(init_function_def, func_callable,
                                            popt)
    status, fitted_y, runtime = \
    parse_result(func_callable, popt, t_start, t_end, data[0])

    return status, fitted_y, fin_func_def, runtime

def chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer_name):

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

    popt, pcov = None, None
    if cost_function == 'least squares':
        popt, pcov = curve_fit(f=function.__call__,
                               xdata=data[0], ydata=data[1], sigma=data[2],
                               p0=initial_params, method=minimizer, maxfev=500)
    elif cost_function == 'unweighted least squares':
        popt, pcov = curve_fit(f=function.__call__,
                               xdata=data[0], ydata=data[1],
                               p0=initial_params, method=minimizer, maxfev=500)
    return popt

def parse_result(function, popt, t_start, t_end, data_x):

    status = 'failed'
    fitted_y, runtime = None, np.nan
    if not popt is None:
        status = 'success'
        fitted_y = get_fittedy(function, data_x, popt)
        runtime = t_end - t_start

    return status, fitted_y, runtime

def get_fin_function_def(init_function_def, func_callable, popt):

    if not 'name=' in str(func_callable):
        popt = list(popt)
        params = init_function_def.split("|")[1]
        params = re.sub(r"[-+]?\d+\.\d+", lambda m, rep=iter(popt):
                        str(round(next(rep), 3)), params)
        fin_function_def = init_function_def.split("|")[0] + " | " + params
        print(fin_function_def)
    else:
        fin_function_def = str(func_callable)

    return fin_function_def

def get_init_function_def(function, mantid_definition):

    if not 'name=' in str(function[0]):
        params = function[0].__code__.co_varnames[1:]
        param_string = ''
        for idx in range(len(function[1])):
            param_string += params[idx] + "= " + str(function[1][idx]) + ", "
        param_string = param_string[:-2]
        init_function_def = function[2] + " | " + param_string
    else:
        init_function_def = mantid_definition

    return init_function_def

def get_fittedy(function, data_x, popt):

    try:
        fitted_y = function.__call__(data_x)
    except:
        fitted_y = function(data_x, *popt)

    return fitted_y


def prepare_data(problem, use_errors):

    data_x = np.copy(problem.data_x)
    data_y = np.copy(problem.data_y)
    data_e = problem.data_e
    data_x, data_y, data_e = misc_preparations(problem, data_x, data_y, data_e)

    if use_errors:
        data = np.array([data_x, data_y, data_e])
        cost_function = 'least squares'
    else:
        data = np.array([data_x, data_y])
        cost_function = 'unweighted least squares'

    return data, cost_function

def misc_preparations(problem, data_x, data_y, data_e):

    if len(data_x) != len(data_y):
        data_x = data_x[:-1]
        problem.data_x = np.copy(data_x)
    if data_e is None:
        data_e = np.sqrt(abs(data_y))
        problem.data_e = np.copy(data_e)

    if problem.start_x is None and problem.end_x is None: pass
    else:
        data_x, data_y, data_e = \
        apply_constraints(problem.start_x, problem.end_x,
                          data_x, data_y, data_e)

    return data_x, data_y, data_e

def apply_constraints(start_x, end_x, data_x, data_y, data_e):

    start_idx = (np.abs(data_x - start_x)).argmin()
    end_idx = (np.abs(data_x - end_x)).argmin()
    data_x = np.copy(data_x[start_idx:end_idx])
    data_y = np.copy(data_y[start_idx:end_idx])
    data_e = np.copy(data_e[start_idx:end_idx])
    data_e[data_e == 0] = 0.000001
    return data_x, data_y, data_e


def function_definitions(problem):

    if problem.type == 'nist':
        return nist_func_definitions(problem.equation, problem.starting_values)
    elif problem.type == 'neutron':
        return neutron_func_definitions(problem.equation)
    else:
        RuntimeError("Your desired algorithm is not supported yet!")


def nist_func_definitions(function, startvals):

    param_names, all_values = get_nist_formula_and_params(startvals)
    function = format_function_scipy(function)
    function_defs = []
    for values in all_values:
        exec "def fitting_function(x, " + param_names + "): return " + function
        function_defs.append([fitting_function, values, function])

    return function_defs

def get_nist_formula_and_params(startvals):

    param_names = [row[0] for row in startvals]
    param_names = ", ".join(param for param in param_names)
    all_values = [row[1] for row in startvals]
    all_values = map(list, zip(*all_values))

    return param_names, all_values

def format_function_scipy(function):

    function = function.replace("exp", "np.exp")
    function = function.replace("^", "**")
    function = function.replace("cos", "np.cos")
    function = function.replace("sin", "np.sin")
    function = function.replace("pi", "np.pi")

    return function


def neutron_func_definitions(functions_string):

    function_names = get_all_neutron_func_names(functions_string)
    function_params = get_all_neutron_func_params(functions_string)
    params = get_neutron_initial_params_values(function_params)
    fit_function = None
    for name in function_names:
        fit_function = make_neutron_fit_function(name, fit_function)

    function_defs = [[fit_function, params]]

    return function_defs

def get_all_neutron_func_names(functions_string):

    functions = functions_string.split(';')
    function_names = []
    for function in functions:
        function_names = get_neutron_func_names(function, function_names)

    return function_names

def get_all_neutron_func_params(functions_string):

    functions = functions_string.split(';')
    function_params = []
    for function in functions:
        function_params = get_neutron_func_params(function, function_params)

    return function_params

def get_neutron_func_names(function, function_names):

    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
    else:
        function_names.append(function[5:])

    return function_names

def get_neutron_func_params(function, function_params):

    first_comma = function.find(',')
    if first_comma != -1:
        function_params.append(function[first_comma+1:])
    else:
        function_params.append('')

    function_params[-1] = function_params[-1].replace(',', ', ')

    return function_params

def get_neutron_initial_params_values(function_params):

    params = []
    for param_set in function_params:
        get_neutron_params(param_set, params)

    params = np.array(params)
    return params

def make_neutron_fit_function(func_name, fit_function):

    func_obj = mantid.gen_func_obj(func_name)
    if fit_function == None: fit_function = func_obj
    else: fit_function += func_obj

    return fit_function

def get_neutron_params(param_set, params):

    start = 0
    while True:
        comma = param_set.find(',', start)
        equal = param_set.find('=', start)
        if param_set[equal-4:equal] == 'ties': break
        if comma == -1: parameter = float(param_set[equal+1:])
        else: parameter = float(param_set[equal+1:comma])
        params.append(parameter)
        if comma == -1: break;
        start = comma + 1

    return params
