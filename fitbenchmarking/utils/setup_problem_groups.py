"""
Utility functions for setting up the problem groups.
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

from parsing.fetch_data import *


def setup(software, data_dir):
    """
    Sets up the problem groups depending on the softwares inputted by the
    user.

    @param software :: software given by user, e.g. mantid
    @param data_dir :: directory holding the problem data used to test
    """
    if software == 'mantid':
        return mantid(data_dir)
    elif software == 'scipy':
        return scipydata(data_dir)
    else:
        raise NameError("Sorry, that application is not supported yet.")

def scipydata(data_dir):
    """
    Set the problem groups for the mantid problem sets.

    @param data_dir :: directory containing all the problem files
                       considered when using the mantid fitting
                       software

    @returns :: the paths to the problem files
    """

    problem_groups = {}
    if 'NIST' in data_dir:
        problem_groups['nist'] = get_nist_problem_files(data_dir)
    elif 'Neutron' in data_dir:
        problem_groups['neutron'] = get_neutron_problem_files(data_dir)
    else:
        raise NameError("Data directory not recognised!")

    return problem_groups

def mantid(data_dir):
    """
    Set the problem groups for the mantid problem sets.

    @param data_dir :: directory containing all the problem files
                       considered when using the mantid fitting
                       software

    @returns :: the paths to the problem files
    """

    problem_groups = {}
    if 'NIST' in data_dir:
        problem_groups['nist'] = get_nist_problem_files(data_dir)
    elif 'Neutron' in data_dir:
        problem_groups['neutron'] = get_neutron_problem_files(data_dir)
    else:
        raise NameError("Data directory not recognised!")

    return problem_groups
