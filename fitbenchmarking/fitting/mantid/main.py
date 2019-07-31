"""
Benchmarking fitting and utility functions for the mantid software.
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

import time
import sys
import numpy as np
import mantid.simpleapi as msapi

from utils.logging_setup import logger
from fitting import misc
from fitting.plotting import plot_helper


MAX_FLOAT = sys.float_info.max


def benchmark(problem, wks_created, function, minimizers, cost_function):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the mantid fitting software.

    @param problem :: a problem object containing information used in fitting
    @param wks_created :: workspace holding the problem data
    @param function :: the fitted function
    @param minimizers :: array of minimizers used in fitting
    @param cost_function :: the cost function used for fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit
    """

    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []

    for minimizer in minimizers:
        status, fit_wks, fin_function_def, runtime = \
            fit(problem, wks_created, function, minimizer, cost_function)
        chi_sq, min_chi_sq, best_fit = \
            chisq(status, fit_wks, min_chi_sq, best_fit, minimizer)
        individual_result = \
            misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                     function, fin_function_def)

        results_problem.append(individual_result)

    return results_problem, best_fit

def fit(problem, wks_created, function, minimizer,
        cost_function='Least squares'):
    """
    The mantid fit software.

    @param problem :: object holding the problem information
    @param wks_created :: workspace holding the problem data
    @param function :: the fitted function
    @param minimizer :: the minimizer used in the fitting process
    @param cost_function :: the type of cost function used in fitting

    @returns :: the status, either success or failure (str), the fit
                workspace (mantid wks_created), containing the
                differences between the fit data and actual data,
                the final function definition
                and how much time it took for the fit to finish (float)
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
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

    status, fit_wks, fin_function_def, runtime = \
        parse_result(fit_result, t_start, t_end)

    return status, fit_wks, fin_function_def, runtime


def chisq(status, fit_wks, min_chi_sq, best_fit, minimizer):
    """
    Function that calculates the chisq obtained through the
    mantid fitting software and find the best fit out of all
    the attempted minimizers.

    @param status :: the status of the fit, i.e. success or failure
    @param fit_wks :: the fit workspace
    @param min_chi_sq :: the minimium chisq (at the moment)
    @param best_fit :: the best fit (at the moment)
    @param minimizer :: minimizer with which the fit_wks was obtained

    @returns :: the chi squared, the new/unaltered minimum chi squared
                and the new/unaltered best fit data object
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

    @param fit_result :: result object from the mantid fitting software
    @param t_start :: time the fitting started
    @param t_end :: time the fitting completed

    @returns :: the processed status (str), fit workspace (mantid wks),
                parameters, errors on them [arrays] and runtime (float).
    """

    status = 'failed'
    fit_wks, fin_function_def, runtime = None, None, np.nan
    if not fit_result is None:
        status = fit_result.OutputStatus
        fit_wks = fit_result.OutputWorkspace
        fin_function_def = str(fit_result.Function)
        runtime = t_end - t_start

    return status, fit_wks, fin_function_def, runtime


def optimum(fit_wks, minimizer_name, best_fit):
    """
    Function that stores the best fit of the given data into
    a object ready for plotting.

    @param fit_wks :: mantid workspace holding the fit data
    @param minimizer_name :: name of the minimizer used in fitting
    @param best_fit :: the previous best_fit object

    @returns :: the new best_fit object
    """

    tmp = msapi.ConvertToPointData(fit_wks)
    best_fit = plot_helper.data(minimizer_name, tmp.readX(1), tmp.readY(1))

    return best_fit


def get_ignore_invalid(problem, cost_function):
    """
    Helper function that sets the whether the mantid fitting software
    ignores invalid data or not. This depends on the cost function.

    @param prob :: object holding the problem information
    @param const_function :: cost function used in fitting

    @returns :: boolean depending on whether to ignore invalid data or not
    """

    ignore_invalid = cost_function == 'Least squares'

    # The WISH data presents some issues
    # For which this ad-hoc if must is present
    if 'WISH17701' in problem.name:
        ignore_invalid = False

    return ignore_invalid
