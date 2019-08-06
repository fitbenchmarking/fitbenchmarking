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
from sasmodels.bumps_model import Experiment, Model
from bumps.names import *
from bumps.fitters import fit as bumpsFit
from fitting.sasview.func_def import get_fin_function_def
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

        model = function[0]
        init_func_def = problem.equation +','+ problem.starting_values
        status, fitted_y, fin_func_def, runtime = \
            fit(problem, data, model, minimizer)
        chi_sq, min_chi_sq, best_fit = \
            chisq(status, data, fitted_y, min_chi_sq, best_fit, minimizer)

        individual_result = \
                misc.create_result_entry(problem, status, chi_sq, runtime, minimizer,
                                     init_func_def, fin_func_def)

        results_problem.append(individual_result)

    return results_problem, best_fit

def fit(problem, data, model, minimizer):
    """

    :param problem:
    :param model:
    :param minimizer:
    :return:
    """

    t_start, t_end = None, None
    exec ("params = dict(" + problem.starting_values + ")")

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
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

    status = 'success' if result.success is True else 'failed'

    fitted_y = func_wrapper.theory()

    fin_func_def = get_fin_function_def(model_wrapper, problem)

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
