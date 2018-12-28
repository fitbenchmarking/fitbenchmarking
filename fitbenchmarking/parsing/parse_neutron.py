"""
Parse input files describing fitting test examples and load the
information into problem objects

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

import os, re
import numpy as np

from utils import fitting_problem
from fitting import mantid
from utils.logging_setup import logger



def load_file(fname):
    """
    Loads a neutron file with all the necessary data.

    @param fname :: path to the neutron problem definition file
                    that is being loaded

    @returns :: problem object containing all the relevant information
    """

    with open(fname) as probf:
        entries = get_neutron_data_problem_entries(probf)
        problem = fitting_problem.FittingProblem()
        data_file = get_data_file(fname, entries['input_file'])
        mantid.store_main_problem_data(data_file, problem)
        store_misc_problem_data(problem, entries)

    return problem


def get_data_file(fname, input_file):
    """
    Gets the path to the neutron data_file used in the problem.
    sep_idx is used to find the last separator in the problem file path
    and set up the path for the data_files folder i.e truncates the path
    to ../Neutron_data and adds ../Neutron_data/data_files

    @param fname :: path to the neutron problem definition file
    @param input_file :: name of the neutron data file

    @returns :: path to the data files directory (str)
    """

    prefix = ""
    if os.sep in fname:
        sep_idx = fname.rfind(os.sep)
        prefix = os.path.join(fname[:sep_idx],"data_files")

    data_file = os.path.join(prefix, input_file)

    return data_file


def get_neutron_data_problem_entries(fname):
    """
    Get the problem entries from a neutron problem definition file.

    @param fname :: path to the neutron problem definition file

    @returns :: a dictionary with all the entires of the problem file
    """

    entries = {}
    for line in fname:
        # Discard comments
        line = line.partition('#')[0]
        line = line.rstrip()
        if not line:
            continue

        lhs, rhs = line.split("=", 1)
        entries[lhs.strip()] = eval(rhs.strip())

    return entries


def store_misc_problem_data(problem, entries):
    """
    Stores the misc data from the problem file into the problem object.

    @param problem :: object holding the problem information
    @param entires :: dictionary containg the entires from the
                      problem definition object
    """

    problem.name = entries['name']
    problem.equation = entries['function']
    problem.starting_values = None
    if 'fit_parameters' in entries:
        problem.start_x = entries['fit_parameters']['StartX']
        problem.end_x = entries['fit_parameters']['EndX']
