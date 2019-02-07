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

import os, glob
from utils.logging_setup import logger

def get_problem_files(data_dir):
    """
    Gets all the problem definition files from the neutron directory.

    @param dirs :: array of directories that contain the problems

    @returns :: array containing paths to all the neutron problems
    """

    probs_all = []
    dirs = sub_dirs(data_dir)
    for directory in dirs:
        search_str = search_string_definition(directory)
        problems = glob.glob(search_str)
        problems.sort()
        for problem in problems:
            logger.info(problem)
        probs_all.append(problems)

    return probs_all

def search_string_definition(directory):
    """
    Either search for text or dat files.
    """
    if 'Neutron' in directory:
        search_str = os.path.join(directory, "*.txt")
    else:
        search_str = os.path.join(directory, "*.dat")

    return search_str

def sub_dirs(directory):
    """
    Check if the folder has any subdirectories.
    """
    subdirs = [x[0] for x in os.walk(directory)]
    subdirs = subdirs[1:]

    if len(subdirs) != 1:
        return subdirs
    else:
        return [directory]

