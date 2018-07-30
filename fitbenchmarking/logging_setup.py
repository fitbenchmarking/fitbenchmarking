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


current_path = os.path.dirname(os.path.realpath(__file__))
fitbenchmarking_path = os.path.abspath(os.path.join(current_path, os.pardir))
scripts_path = os.path.join(fitbenchmarking_path, 'fitbenchmarking')
logs_path = os.path.join(scripts_path, 'logs')

if not os.path.exists(logs_path):
    os.makedirs(logs_path)

FORMATTER='%(asctime)s %(name)s %(levelname)s: %(message)s'

formatter = logging.Formatter(FORMATTER, "%H:%M:%S")
handler = logging.FileHandler(logs_path + os.sep + 'fitbenchmarking.log', mode='w')
handler.setFormatter(formatter)
logger = logging.getLogger('fitbenchmarking')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
