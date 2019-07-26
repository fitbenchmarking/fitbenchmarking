"""
To be added
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

from mantid.api import *
import numpy as np

main_func = None
class fitFunction(IFunction1D):

    def init(self):
        self.declareParameter("x", 2.5, "x")

    def getFunction(self, function):
        global main_func
        main_func = function

    def function1D(self, x, params):

        global main_func

        parm_string = ''
        for parm in params:
            parm_string += ','+ str(parm)

        parm_string += ')'

        result = eval('main_func(x' + parm_string)

        return result

FunctionFactory.subscribe(fitFunction)




