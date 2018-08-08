"""
Mantid fitting utility functions.
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
from plotting import plotHelper


def parse_result(fit_result):
    """
    DESC
    """

    status = 'failed'
    fit_wks, params, errors, runtime = None, None, None, np.nan
    if not fit_result is None:
        status = fit_result.OutputStatus
        fit_wks = fit_result.OutputWorkspace
        params = fit_result.OutputParameters.column(1)[:-1]
        errors = fit_result.OutputParameters.column(2)[:-1]
        runtime = t_end - t_start

    return status, fit_wks, params, errors, runtime


def optimum(fit_wks, minimizer_name, best_fit):
    """
    DESC
    """

    tmp = msapi.ConvertToPointData(fit_wks)
    best_fit = plotHelper.data(minimizer_name, tmp.readX(1), tmp.readY(1))

    return  best_fit


def wks_cost_function(prob, use_errors):
    """
    DESC
    """

    if use_errors:
        data_e = setup_errors(prob)
        wks = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y,
                                    DataE=data_e)
        cost_function = 'Least squares'
    else:
        wks = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y)
        cost_function = 'Unweighted least squares'

    return wks, cost_function


def function_definitions(prob):
    """
    DESC
    """

    if prob.starting_values:
        # NIST data requires prior formatting
        nb_start_vals = len(prob.starting_values[0][1])
        function_defs = parse_nist_function_definitions(prob, nb_start_vals)
    else:
        # Neutron data does not require any
        function_defs = []
        function_defs.append(prob.equation)

    return function_defs


def ignore_invalid(prob, cost_function):
    """
    DESC
    """

    ignore_invalid = cost_function == 'Least squares'
    if 'WISH17701' in prob.name:
        ignore_invalid = False

    return ignore_invalid


def parse_nist_function_definitions(prob, nb_start_vals):
    """
    DESC
    """

    function_defs = []
    for start_idx in range(0, nb_start_vals):
        start_val_str = ''

        for param in prob.nb_start_vals:
            start_val_str += ('{0}={1},'.format(param[0], param[1][start_idx]))
            function_defs.append("name=UserFunction, Formula={0}, {1}".
                                 format(prob.equation, start_val_str))
    return function_defs


def setup_errors(prob):
    """
    DESC
    """

    data_e = None
    if prob.data_pattern_obs_errors is None:
        data_e = np.sqrt(abs(prob.data_y))
    else:
        data_e = prob.data_pattern_obs_errors

    return data_e
