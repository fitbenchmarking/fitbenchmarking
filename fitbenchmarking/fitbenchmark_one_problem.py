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
from fitting import misc
from fitting.plotting import plots

from utils.logging_setup import logger


def fitbm_one_problem(algorithm, problem, minimizers, use_errors=True,
                      group_results_dir=None):
    """
    Sets up the workspace, cost function and function definitons for
    a particular problem and fits the models provided in the problem
    object. The best fit, along with the data and a starting guess
    is then plotted on a visual display page.

    @param algorithm :: algorithm used in fitting the problem, can be
                        e.g. mantid, numpy etc.
    @param problem :: a problem object containing information used in fitting
    @param minimizers :: array of minimizers used in fitting
    @param use_errors :: whether to use errors or not
    @param group_results_dir :: directory in which the group results
                                are saved

    @returns :: nested array of result objects, per function definition
                containing the fit information
    """

    previous_name, count = None, 0
    results_fit_problem = []
    data_struct, cost_function, function_definitions = \
    misc.prepare_algorithm_prerequisites(algorithm, problem, use_errors)

    for function in function_definitions:
        results_problem, best_fit = \
        fit_one_function_def(algorithm, problem, data_struct, function,
                             minimizers, cost_function)

        if not best_fit is None:
            previous_name, count = \
            plots.make_plots(algorithm, problem, data_struct, function,
                             best_fit, previous_name, count, group_results_dir)

        results_fit_problem.append(results_problem)

    return results_fit_problem


def fit_one_function_def(algorithm, problem, data_struct, function, minimizers,
                         cost_function):
    """
    Fits a given function definition (model) to the data in the workspace.

    @param algorithm :: algorithm used in fitting the problem, can be
                        e.g. mantid, numpy etc.
    @param problem :: a problem object containing information used in fitting
    @param data_struct :: a structre in which the data to be fitted is
                          stored, can be e.g. mantid workspace, np array etc.
    @param function :: analytical function string that is fitted
    @param minimizers :: array of minimizers used in fitting
    @param cost_function :: the cost function used for fitting

    @returns :: nested array of result objects, per minimizer
                and data object for the best fit
    """

    if algorithm == 'mantid':
        return mantid.benchmark(problem, data_struct, function, minimizers,
                                cost_function)
    else:
        raise NameError("Sorry, that algorithm is not supported.")



