"""
Fit benchmark one problem functions.
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

import sys
import numpy as np
import mantid.simpleapi as msapi


from fitting import mantid
from fitting.plotting import plots
from utils import test_result
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max


def fitbm_one_problem(prob, minimizers, use_errors=True,
                      group_results_dir=None):
    """
    Sets up the workspace, cost function and function definitons for
    a particular problem and fits the models provided in the problem
    object. The best fit, along with the data and a starting guess
    is then plotted on a visual display page.

    @param prob :: a problem object containing information used in fitting
    @param minimizers :: array of minimizers used in fitting
    @param use_errors :: whether to use errors or not
    @param group_results_dir :: directory in which the group results
                                are saved

    @returns :: nested array of result objects, per function definition
                containing the fit information
    """

    previous_name, count = None, 0
    results_fit_problem = []
    wks, cost_function = mantid.wks_cost_function(prob, use_errors)
    function_definitions = mantid.function_definitions(prob)

    for function in function_definitions:
        results_problem, best_fit = \
        fit_one_function_def(prob, wks, function, minimizers, cost_function)

        if not best_fit is None:
            previous_name, count = \
            plots.make_plots(prob, wks, function, best_fit, previous_name,
                             count, group_results_dir)

        results_fit_problem.append(results_problem)

    return results_fit_problem


def fit_one_function_def(prob, wks, function, minimizers, cost_function):
    """
    Fits a given function definition (model) to the data in the workspace.

    @param prob :: a problem object containing information used in fitting
    @param wks :: mantid workspace containing data to be fitted
    @param function :: analytical function string that is fitted
    @param minimizers :: array of minimizers used in fitting
    @param cost_function :: the cost function used for fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit
    """

    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []
    for minimizer in minimizers:

        status, fit_wks, fin_function_def, runtime = \
        mantid.fit(prob, wks, function, minimizer, cost_function)
        chi_sq, min_chi_sq, best_fit = \
        mantid.chisq(status, fit_wks, min_chi_sq, best_fit, minimizer)
        result = create_result_entry(prob, status, chi_sq, runtime, minimizer,
                                     function, fin_function_def)
        results_problem.append(result)

    return results_problem, best_fit


def create_result_entry(prob, status, chi_sq, runtime, minimizer,
                        ini_function_def, fin_function_def):
    """
    Helper function that creates a result object after fitting a problem
    with a certain function and minimzier.

    @param prob :: problem object containing info that was fitted
    @param status :: status of the fit, i.e. success or failure
    @param chi_sq :: the chi squared of the fit
    @param runtime :: the runtime of the fit
    @param minimizer :: the minimizer used for this particular fit
    @param function :: the function used for this particular fit

    @returns :: the result object
    """

    # Create empty fitting result object
    result = test_result.FittingTestResult()

    # Populate result object
    result.problem = prob
    result.fit_status = status
    result.chi_sq = chi_sq
    result.runtime = runtime
    result.minimizer = minimizer
    result.ini_function_def = ini_function_def
    result.fin_function_def = fin_function_def

    return result
