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

import numpy as np
import mantid.simpleapi as msapi

from make_plots, fitting_algorithms, utils_fit, utils_mantid_fit import *
from logging_setup import logger

import test_result
MAX_FLOAT = sys.float_info.max


def fitbenchmark_one_problem(prob, minimizers, use_errors=True, count=0,
                             group_results_dir):
    """
    """

    previous_name = None
    results_fit_problem = []
    wks, cost_function = mantid_wks_cost_function(prob, use_errors)
    function_definitions = mantid_function_definitions(prob)

    for function in function_definitions:
        results_problem, best_fit = \
        fit_one_function_def(prob, wks, function, minimizers, cost_function)

        if not best_fit is None:
            previous_name, count = \
            make_plots(prob, wks, function, best_fit, previous_name, count,
                       group_results_dir)

        results_fit_problem.append(results_problem)

    return results_fit_problem


def fit_one_function_def(prob, wks, function, minimizers, cost_function):
    """
    """
    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []
    for minimizer_name in minimizers:

        status, params, errors, fit_wks, runtime = \
        mantid_fit(prob, wks, function, minimizer_name, cost_function)
        chi_sq = calculate_chi_sq(fit_wks.readY(2))
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = mantid_optimal_fit(fit_wks, minimizer_name, best_fit)
            min_chi_sq = chi_sq

        result = store_results(prob, status, params, errors, chi_sq, runtime,
                               minimizer_name, function)
        results_problem.append(result)

    return results_problem, best_fit


def store_results(prob, status, params, errors, chi_sq, runtime,
                  minimizer_name, function):
    """
    """
    result = test_result.FittingTestResult()
    result.problem = prob
    result.fit_status = status
    result.params = params
    result.errors = errors
    result.chi_sq = chi_sq
    result.runtime = runtime
    result.minimizer = minimizer_name
    result.function_def = function

    return result







