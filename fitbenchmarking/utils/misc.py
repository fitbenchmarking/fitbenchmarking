"""
Miscellaneous functions and utilities used in fitting benchmarking.
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


def get_minimizers(software_options):
    """
    Gets an array of minimizers to fitbenchmark from the json file depending
    on which software is used.
    @param software_options :: dictionary containing software used in fitting the problem and list of minimizers or location of json file contain minimizers
    @returns :: an array of strings containing minimizer names and software used
    """
    try:

        software = software_options['software']
        minimizer_options = software_options['minimizer_options']
        if not isinstance(software, list):
            software = [software]
        minimizers = []
        for x in software:
            if not minimizer_options:
                current_path = os.path.dirname(os.path.realpath(__file__))
                fitbm_path = os.path.abspath(os.path.join(current_path, os.pardir))
                minimizer_file = os.path.join(fitbm_path,
                                              "minimizers_list_default.json")
                minimizers_list = json.load(open(minimizer_file))
            elif isinstance(minimizer_options, str):
                minimizers_list = json.load(open(minimizer_options))
            elif isinstance(minimizer_options, dict):
                minimizers_list = minimizer_options
            else:
                raise ValueError('minimizer_options required to be None, string '
                                 'or dictionary, type(minimizer_options) '
                                 '= {}'.format(type(minimizer_options)))
            minimizers.append(minimizers_list[x])
    except:
        raise ValueError('software_options required to be a dictionary with '
                         'keys software and minimizer_options')
    if len(software) > 1:
        return minimizers, software

    else:
        return minimizers[0], software[0]


def setup_fitting_problems(data_dir, group_name):
    """
    Sets up the problem groups specified by the user by providing
    a respective data directory.

    @param data_dir :: directory holding the problem data used to test
    @returns :: the problem groups dictionary
    """
    problem_groups = {}
    problem_groups[group_name] = get_problem_files(data_dir)

    return problem_groups


def save_user_input(software, minimizers, group_name, results_dir, use_errors):
    """
    All parameters inputed by the user are stored in an object.
    @params :: please check the user_input.py file in the utils dir.
    @returns :: an object containing all the information specified by the user.
    """

    uinput = user_input.UserInput()
    uinput.software = software
    uinput.minimizers = minimizers
    uinput.group_name = group_name
    uinput.group_results_dir = results_dir
    uinput.use_errors = use_errors

    return uinput
