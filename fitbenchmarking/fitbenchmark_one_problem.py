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


from fitting import fit_algorithms, mantid_utils
from fitting.plotting import plots
from utils import fit_misc, test_result
from utils.logging_setup import logger

MAX_FLOAT = sys.float_info.max


def fitbm_one_problem(prob, minimizers, use_errors=True, group_results_dir=None):
    """
    """

    previous_name, count = None, 0
    results_fit_problem = []
    wks, cost_function = mantid_utils.wks_cost_function(prob, use_errors)
    function_definitions = mantid_utils.function_definitions(prob)

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
    """

    min_chi_sq, best_fit = MAX_FLOAT, None
    results_problem = []
    for minimizer in minimizers:

        status, fit_wks, params, errors, runtime = \
        fit_algorithms.mantid(prob, wks, function, minimizer, cost_function)
        chi_sq, min_chi_sq, best_fit = mantid_chisq(status, fit_wks, min_chi_sq,
                                                    best_fit, minimizer)
        result = store_results(prob, status, params, errors, chi_sq, runtime,
                               minimizer, function)
        results_problem.append(result)

    return results_problem, best_fit


def mantid_chisq(status, fit_wks, min_chi_sq, best_fit, minimizer):
    """
    """

    if status != 'failed':
        chi_sq = fit_misc.compute_chisq(fit_wks.readY(2))
        if chi_sq < min_chi_sq and not chi_sq == np.nan:
            best_fit = mantid_utils.optimum(fit_wks, minimizer, best_fit)
            min_chi_sq = chi_sq
    else:
        chi_sq = np.nan

    return chi_sq, min_chi_sq, best_fit


def store_results(prob, status, params, errors, chi_sq, runtime,
                  minimizer, function):
    """
    """
    result = test_result.FittingTestResult()
    result.problem = prob
    result.fit_status = status
    result.params = params
    result.errors = errors
    result.chi_sq = chi_sq
    result.runtime = runtime
    result.minimizer = minimizer
    result.function_def = function

    return result
