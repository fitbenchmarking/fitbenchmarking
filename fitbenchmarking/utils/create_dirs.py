"""
Utility functions for creating/deleting directories.
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

import os
import sys
import shutil


def results(results_dir):
    """
    Creates the results folder where the script that is run in the
    console and eventually calls this is located.

    @param results_dir :: path to the results directory, results dir
                          name or None

    @returns :: proper path to the results directory
    """

    working_dir = os.getcwd()
    if results_dir is None:
        results_dir = os.path.join(working_dir, "results")
    elif not isinstance(results_dir, str):
        raise TypeError("results_dir must be a string!")
    elif not os.sep in results_dir:
        results_dir = os.path.join(working_dir, results_dir)

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    return results_dir

def group_results(results_dir, group_name):
    """
    Creates the group results folder into the main results directory.

    @param results_dir :: path to the results directory, results dir
                          name or None
    @group_name :: name of the problem group that is currently
                   being processed

    @returns :: proper path to the group results directory
    """

    group_results_dir = os.path.join(results_dir, group_name)
    if os.path.exists(group_results_dir):
        del_contents_of_dir(group_results_dir)
    else:
        os.makedirs(group_results_dir)

    return group_results_dir

def restables_dir(results_dir, group_name):
    """
    Creates the results directory where the tables are located.
    e.g. fitbenchmarking/results/neutron/

    @param results_dir :: directory that holds all the results
    @param group_name :: string containing the name of the problem group

    @returns :: path to folder where the tables are stored
    """

    if 'nist' in group_name:
        group_results_dir = os.path.join(results_dir, 'nist')
        if not os.path.exists(group_results_dir):
            os.makedirs(group_results_dir)
        tables_dir = os.path.join(group_results_dir, group_name)

    elif 'neutron' in group_name:
        group_results_dir = os.path.join(results_dir, 'neutron')
        tables_dir = group_results_dir

    if not os.path.exists(tables_dir):
        os.makedirs(tables_dir)

    return tables_dir

def figures(group_results_dir):
    """
    Creates the figures directory inside the support_pages directory.

    @param group_results_dir :: path to the group results directory

    @returns :: path to the figures directory
    """

    support_pages_dir = \
    os.path.join(group_results_dir, "support_pages")
    if not os.path.exists(support_pages_dir):
            os.makedirs(support_pages_dir)
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)

    return figures_dir

def del_contents_of_dir(directory):
    """
    Delete contents of a directory, including other directories.

    @param directory :: the target directory
    """

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
