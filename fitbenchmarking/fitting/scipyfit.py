"""
Fittng and utility functions for the scipy fitting software.
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
                               xdata=data[0], ydata=data[1], sigma=data[2],
                               p0=initial_params, method=minimizer, maxfev=500)
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

def get_fin_function_def(init_function_def, func_callable, popt):
    """
    Produces the final function definition.

    @param init_function_def :: the initial function definition string
    @param func_callable :: callable function object
    @param popt :: array containing the values of the function variables
                   after the fit was performed

    @returns :: the final function definition string
    """
    if not 'name=' in str(func_callable):
        popt = list(popt)
        params = init_function_def.split("|")[1]
        params = re.sub(r"[-+]?\d+\.\d+", lambda m, rep=iter(popt):
                        str(round(next(rep), 3)), params)
        fin_function_def = init_function_def.split("|")[0] + " | " + params
    else:
        fin_function_def = str(func_callable)

    return fin_function_def

def get_init_function_def(function, mantid_definition):
    """
    Get the initial function definition string.

    @param function :: array containing the function information
    @param mantid_definition :: the string containing the function
                                definition in mantid format

    @returns :: the initial function defintion string
    """
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
    """
    Gets the fitted y data corresponding to given x values.
    """
    try:
        fitted_y = function.__call__(data_x)
    except:
        fitted_y = function(data_x, *popt)

    return fitted_y


def prepare_data(problem, use_errors):
    """
    Prepares the data to be used in the fitting process.
    """
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
    """
    Helper function that does some miscellaneous preparation of the data.
    It calculates the errors if they are not presented in problem file
    itself by assuming a Poisson distribution. Additionally, it applies
    constraints to the data if such constraints are provided.
    """
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
    """
    Applied constraints to the data if they are provided. Useful when
    fitting only part of the available data.
    """
    start_idx = (np.abs(data_x - start_x)).argmin()
    end_idx = (np.abs(data_x - end_x)).argmin()
    data_x = np.copy(data_x[start_idx:end_idx])
    data_y = np.copy(data_y[start_idx:end_idx])
    data_e = np.copy(data_e[start_idx:end_idx])
    data_e[data_e == 0] = 0.000001
    return data_x, data_y, data_e


def function_definitions(problem):
    """
    Processing the function definitions into an appropriate format for
    the softwareto understand.
    """
    if problem.type == 'nist':
        return nist_func_definitions(problem.equation, problem.starting_values)
    elif problem.type == 'neutron':
        return neutron_func_definitions(problem.equation)
    else:
        RuntimeError("Your problem type is not supported yet!")


# -----------------------------------------------------------------------------
def nist_func_definitions(function, startvals):
    """
    Processing the nist function definitions into an appropriate format
    for the scipy softwareto use.

    @param function :: function string as defined in the problem file
    @param startvals :: starting values for the function variables
                        provided in the problem definition file

    @returns :: array containing the fitting_function callable by scipy,
                values of the parameters and the function string
    """
    param_names, all_values = get_nist_param_names_and_values(startvals)
    function = format_function_scipy(function)
    function_defs = []
    for values in all_values:
        exec "def fitting_function(x, " + param_names + "): return " + function
        function_defs.append([fitting_function, values, function])

    return function_defs

def get_nist_param_names_and_values(startvals):
    """
    Parses startvals and retrieves the nist param names and values.
    """
    param_names = [row[0] for row in startvals]
    param_names = ", ".join(param for param in param_names)
    all_values = [row[1] for row in startvals]
    all_values = map(list, zip(*all_values))

    return param_names, all_values

def format_function_scipy(function):
    """
    Formats the function string such that it is scipy-ready.
    """

    function = function.replace("exp", "np.exp")
    function = function.replace("^", "**")
    function = function.replace("cos", "np.cos")
    function = function.replace("sin", "np.sin")
    function = function.replace("pi", "np.pi")

    return function
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
def neutron_func_definitions(functions_string):
    """
    Processing the neutron function definition into an appropriate format
    for the scipy softwareto use.

    @param function_string :: string defining the function in
                              mantid format

    @returns :: function definition array containing a mantid function
                callable and the function parameter values respectively
    """

    function_names = get_all_neutron_func_names(functions_string)
    function_params = get_all_neutron_func_params(functions_string)
    params, ties = get_neutron_initial_params_values(function_params)
    fit_function = None
    for name in function_names:
        fit_function = make_neutron_fit_function(name, fit_function)
    fit_function = mantid.set_ties(fit_function, ties)

    function_defs = [[fit_function, params]]

    return function_defs

def get_all_neutron_func_names(functions_string):
    """
    Helper function that parses the function_string and retrieves
    all the function names to be fitted.
    """

    functions = functions_string.split(';')
    function_names = []
    for function in functions:
        function_names = get_neutron_func_names(function, function_names)

    return function_names

def get_all_neutron_func_params(functions_string):
    """
    Helper function that parses the function_string and retrieves all
    the function parameters.
    """
    functions = functions_string.split(';')
    function_params = []
    for function in functions:
        function_params = get_neutron_func_params(function, function_params)

    return function_params

def get_neutron_func_names(function, function_names):
    """
    Helper function that retrieves the function name of only
    one function.
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_names.append(function[5:first_comma])
    else:
        function_names.append(function[5:])

    return function_names

def get_neutron_func_params(function, function_params):
    """
    Helper function that retrieves the function parameters of only
    one function.
    """
    first_comma = function.find(',')
    if first_comma != -1:
        function_params.append(function[first_comma+1:])
    else:
        function_params.append('')

    function_params[-1] = function_params[-1].replace(',', ', ')

    return function_params

def get_neutron_initial_params_values(function_params):
    """
    Parses the function_params string and puts only the initial parameter
    values into a numpy array to be used by scipy.
    """
    params = []
    ties = []
    for param_set in function_params:
        get_neutron_params(param_set, params)
        get_neutron_ties(param_set, ties)

    params = np.array(params)
    return params, ties

def make_neutron_fit_function(func_name, fit_function):
    """
    Create the neutron fit function object that is used by scipy.
    """
    func_obj = mantid.gen_func_obj(func_name)
    if fit_function == None: fit_function = func_obj
    else: fit_function += func_obj

    return fit_function

def get_neutron_params(param_set, params):
    """
    Get the neutron param values from the param_set string array which
    may contain multiple parameter sets (for each function).
    """
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

def get_neutron_ties(param_set, ties):
    """
    Gets the neutron problem tie values.
    """
    start = param_set.find("ties=") + 5
    ties_per_function = []
    while True:
        if start == 4: break
        comma = param_set.find(',', start+1)
        if comma != -1: tie = param_set[start+1:comma]
        else: tie = param_set[start+1:comma]
        ties_per_function.append(tie.replace("=","': "))
        if comma == -1: break;
        start = comma + 1

    ties.append(ties_per_function)

    return ties
# -----------------------------------------------------------------------------
