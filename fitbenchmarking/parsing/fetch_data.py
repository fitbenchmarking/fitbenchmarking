"""
Functions that fetch the problem files.
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

import os
import glob
from utils.logging_setup import logger


def get_problem_files(data_dir):
    """
    Gets all the problem definition files from the neutron directory.

    @param dirs :: array of directories that contain the problems

    @returns :: array containing paths to all the problems
    """
    probs_all = []
    dirs = filter(os.path.isdir, os.listdir(data_dir))
    if dirs == [] or dirs == ['data_files']:
        dirs.insert(0, data_dir)
    for directory in dirs:
        test_data = glob.glob(directory + '/*.*')
        problems = [os.path.join(directory, data) for data in test_data]
        problems.sort()
        for problem in problems:
            logger.info(problem)
        probs_all.append(problems)

    return probs_all
