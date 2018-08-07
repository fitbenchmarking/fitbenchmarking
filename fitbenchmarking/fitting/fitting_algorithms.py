"""
Fitting algorithms.
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
import mantid.simpleapi as msapi

from logging_setup import logger
from utils_mantid_fit import mantid_set_ignore_invalid, mantid_parse_result


def mantid_fit(prob, wks, function, minimizer='Levenberg-Marquardt',
               cost_function='Least squares'):
    """
    """

    fit_result = None
    try:
        ignore_invalid = mantid_set_ignore_invalid(prob, cost_function)
        t_start = time.clock()
        fit_result = msapi.Fit(function, wks, Output='ws_fitting_test',
                               Minimizer=minimizer, CostFunction=cost_function,
                               IgnoreInvalidData=ignore_invalid,
                               StartX=prob.start_x, EndX=prob.end_x)
        t_end = time.clock()
    except (RuntimeError, ValueError) as err:
        logger.error("Warning, fit failed. Going on. Error: " + str(err))

    status, fit_wks, params, errors, runtime = \
    mantid_parse_result(fit_result, t_end, t_start)

    return status, fit_wks, params, errors, runtime
