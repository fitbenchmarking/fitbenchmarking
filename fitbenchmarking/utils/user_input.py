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


class UserInput(object):
    """
    Structure to hold all the user inputted data.
    """

    def __init__(self):
        # The software that is benchmarked e.g. scipy, mantid etc.
        self.software = None
        # The minimizers inside that certain software that are
        # being benchmarked
        self.minimizers = None
        # The name of the problem group to be analysed e.g. neutron
        self.group_name = None
        # Director path in which to put the results for each problem group
        self.group_results_dir = None
        # Whether or not to consider error bars in the fitting process
        self.use_errors = None
