"""
Utility functions to support logging for the fitbenchmarking
algorithm.
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
# File change history is stored at: <https://github.com/mantidproject/mantid>.
# Code Documentation is available at: <http://doxygen.mantidproject.org>

from __future__ import (absolute_import, division, print_function)

import os
import logging


if not os.path.exists('logs'):
    os.makedirs('logs')

FORMATTER='%(asctime)s %(name)s %(levelname)s: %(message)s'

formatter = logging.Formatter(FORMATTER, "%H:%M:%S")
handler = logging.FileHandler('logs' + os.sep + 'fitbenchmarking.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger('fitbenchmarking')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
