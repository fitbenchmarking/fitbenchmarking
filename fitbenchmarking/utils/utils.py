"""
General utility functions.
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

import os, sys, shutil

def empty_contents_of_folder(directory):
    """
    """

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def setup_group_results_dir(results_dir, group_name):
    """
    """

    group_results_dir = os.path.join(results_dir, group_name)
    if os.path.exists(group_results_dir):
        empty_contents_of_folder(group_results_dir)
    else:
        os.makedirs(group_results_dir)

    return group_results_dir


def setup_results_dir(results_dir):
    """
    """

    working_dir = os.getcwd()
    if results_dir is None:
        results_dir = os.path.join(working_dir, "results")
    elif not isinstance(results_dir, str):
        TypeError("results_dir must be a string!")
    elif not os.sep in results_dir:
        results_dir = os.path.join(working_dir, results_dir)
    else:
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

    return results_dir


def setup_figures_dirs(group_results_dir):
    """
    """

    support_pages_dir = \
    os.path.join(group_results_dir, "tables", "support_pages")
    if not os.path.exists(support_pages_dir):
            os.makedirs(support_pages_dir)
    figures_dir = os.path.join(support_pages_dir, "figures")
    if not os.path.exists(figures_dir):
        os.makedirs(figures_dir)
