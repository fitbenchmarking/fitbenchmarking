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

from utils import test_problem
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
        prob = test_problem.FittingTestProblem()
        data_files_dir = get_data_files_dir(fname, entries['input_file'])
        store_main_problem_data(data_files_dir, prob)
        store_misc_problem_data(prob, entries)

    return prob


def get_data_files_dir(fname, input_file):
    """
    Gets the path to the neutron data_files dir.
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

    data_files_dir = os.path.join(prefix, input_file)

    return data_files_dir


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


def store_main_problem_data(fname, prob):
    """
    Stores the main problem data into the relevant attributes of the
    problem object.

    @param fname :: path to the neutron problem definition file
    @param prob :: object holding the problem information
    """

    import mantid.simpleapi as msapi

    wks = msapi.Load(Filename=fname)
    prob.data_x = wks.readX(0)
    prob.data_y = wks.readY(0)
    prob.data_pattern_obs_errors = wks.readE(0)
    prob.ref_residual_sum_sq = 0


def store_misc_problem_data(prob, entries):
    """
    Stores the misc data from the problem file into the problem object.

    @param prob :: object holding the problem information
    @param entires :: dictionary containg the entires from the
                      problem definition object
    """

    prob.name = entries['name']
    prob.equation = entries['function']
    prob.starting_values = None
    if 'fit_parameters' in entries:
        prob.start_x = entries['fit_parameters']['StartX']
        prob.end_x = entries['fit_parameters']['EndX']
