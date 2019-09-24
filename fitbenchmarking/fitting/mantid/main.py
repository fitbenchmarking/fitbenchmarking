"""
Benchmarking fitting and utility functions for the mantid software.
"""

from __future__ import (absolute_import, division, print_function)

import time
import sys
import numpy as np
import mantid.simpleapi as msapi

from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.fitting import misc
from fitbenchmarking.fitting.plotting import plot_helper


MAX_FLOAT = sys.float_info.max


def benchmark(problem, wks_created, function, minimizers, cost_function):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the mantid fitting software.

    :param problem: A problem object containing information used in fitting
    :type problem: object
    :param wks_created: Workspace holding the problem data
    :type wks_created: mantid workspace
    :param function: The fitted function
    :type function: string
    :param minimizers: Array of minimizers used in fitting
    :type minimizers: list of string
    :param cost_function: The cost function used for fitting
    :type cost_function: string

    :return: Results per minimizer and data object for the best fit
    :rtype: nested list of results objects
    """

    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []

    for minimizer in minimizers:
        status, fit_wks, fin_function_def, runtime = \
            fit(problem, wks_created, function, minimizer, cost_function)
        chi_sq, min_chi_sq, best_fit = \
            chisq(status, fit_wks, min_chi_sq, best_fit, minimizer)
        individual_result = \
            misc.create_result_entry(problem, status, chi_sq, runtime,
                                     minimizer, function, fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit


def fit(problem, wks_created, function, minimizer,
        cost_function='Least squares'):
    """
    The mantid fit software.

    :param problem: Object holding the problem information
    :type problem: object
    :param wks_created: Workspace holding the problem data
    :type wks_created: mantid workspace
    :param function: The fitted function
    :type function: string
    :param minimizer: The minimizer used in the fitting process
    :type minimizer: string
    :param cost_function: The type of cost function used in fitting
    :type cost_function: string

    :return: the status, either success or failure,
             the fit workspace, containing the
                 differences between the fit data and actual data,
             the final function definition
             runtime of the fitting
    :rtype: string, mantid workspace, string, float
    """
    fit_result, t_start, t_end = None, None, None
    try:
        ignore_invalid = get_ignore_invalid(problem, cost_function)
        t_start = time.clock()
        fit_result = msapi.Fit(function, wks_created, Output='ws_fitting_test',
                               Minimizer=minimizer, CostFunction=cost_function,
                               IgnoreInvalidData=ignore_invalid,
                               StartX=problem.start_x, EndX=problem.end_x)
        t_end = time.clock()
    except (RuntimeError, ValueError) as err:
        logger.warning("Fit failed: " + str(err))

    status, fit_wks, fin_function_def, runtime = \
        parse_result(fit_result, t_start, t_end)

    return status, fit_wks, fin_function_def, runtime


def chisq(status, fit_wks, min_chi_sq, best_fit, minimizer):
    """
    Function that calculates the chisq obtained through the
    mantid fitting software and find the best fit out of all
    the attempted minimizers.

    :param status: The status of the fit, i.e. success or failure
    :type status: string
    :param fit_wks: The fit workspace
    :type fit_ws: mantid workspace
    :param min_chi_sq: The minimium chisq (at the moment)
    :type min_chi_sq: float
    :param best_fit: The best fit (at the moment)
    :type best_fit: object
    :param minimizer: Minimizer with which the fit_wks was obtained
    :type minimizer: string

    :return: the chi squared, the new/unaltered minimum chi squared
             and the new/unaltered best fit data object
    :rtype: float, float, object
    """

    if status != 'failed':
        chi_sq = misc.compute_chisq(fit_wks.readY(2))
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = optimum(fit_wks, minimizer, best_fit)
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan

    return chi_sq, min_chi_sq, best_fit


def parse_result(fit_result, t_start, t_end):
    """
    Function that takes the raw result from the mantid fitting software
    and refines it.

    :param fit_result: Result object from the mantid fitting software
    :type fit_result: object
    :param t_start: Time the fitting started
    :type t_start: float
    :param t_end: Time the fitting completed
    :type t_end: float

    :return: The processed status (str), fit workspace (mantid wks),
             the final function def (str), and runtime (float).
    :rtype: string, mantid workspace, string, runtime
    """

    status = 'failed'
    fit_wks, fin_function_def, runtime = None, None, np.nan
    if fit_result is not None:
        status = fit_result.OutputStatus
        fit_wks = fit_result.OutputWorkspace
        fin_function_def = str(fit_result.Function)
        runtime = t_end - t_start
    return status, fit_wks, fin_function_def, runtime


def optimum(fit_wks, minimizer_name, best_fit):
    """
    Function that stores the best fit of the given data into
    a object ready for plotting.

    :param fit_wks: Mantid workspace holding the fit data
    :type fit_ws: mantid workspace
    :param minimizer_name: Name of the minimizer used in fitting
    :type minimizer_name: string
    :param best_fit: The previous best_fit object
    :type best_fit: object

    :return: The new best_fit object
    :rtype: object
    """

    tmp = msapi.ConvertToPointData(fit_wks)
    best_fit = plot_helper.data(minimizer_name, tmp.readX(1), tmp.readY(1))

    return best_fit


def get_ignore_invalid(problem, cost_function):
    """
    Helper function that sets the whether the mantid fitting software
    ignores invalid data or not. This depends on the cost function.

    :param prob: Object holding the problem information
    :type prob: object
    :param const_function: Cost function used in fitting
    :type const_function: string

    :return: Boolean depending on whether to ignore invalid data or not
    :rtype: bool
    """

    ignore_invalid = cost_function == 'Least squares'

    # The WISH data presents some issues
    # For which this ad-hoc if must is present
    if 'WISH17701' in problem.name:
        ignore_invalid = False

    return ignore_invalid
