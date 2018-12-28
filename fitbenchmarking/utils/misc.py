"""
Miscellaneous functions and utilites used in fitting benchmarking.
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
import json

from parsing.fetch_data import *
from utils import user_input


def get_minimizers(software):
    """
    Gets an array of minimizers to fitbenchmark from the json file depending
    on which software is used.

    @param software :: string defining the software used

    @returns :: an array of strings containing minimizer names
    """

    current_path = os.path.dirname(os.path.realpath(__file__))
    fitbm_path = os.path.abspath(os.path.join(current_path, os.pardir))
    minimizers_json = os.path.join(fitbm_path, "minimizers.json")
    all_minimizers = json.load(open(minimizers_json))
    minimizers = all_minimizers[software]

    return minimizers


def setup_fitting_problems(data_dir):
    """
    Sets up the problem groups specified by the user by providing
    a respective data directory.

    @param data_dir :: directory holding the problem data used to test

    @returns :: the problem groups dictionary
    """

    if 'NIST' in data_dir:
        problem_groups['nist'] = get_nist_problem_files(data_dir)
    elif 'Neutron' in data_dir:
        problem_groups['neutron'] = get_neutron_problem_files(data_dir)
    else:
        raise NameError("Data directory not recognised!")

    return problem_groups

def save_user_iput(software, minimizers, group_name, use_errors, results_dir):
    """
    All parameters inputed by the user are stored in an object.

    @params :: please check the user_input.py file in the utils dir.

    @returns :: an object containing all the information specified by the user.
    """

    uinput = user_input.UserInput()
    uinput.software = software
    uinput.minimizers = minimizers
    uinput.group_name = gorup_name
    uinput.results_dir = results_dir
    uinput.use_errors = use_errors

    return uinput
