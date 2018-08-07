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
from logging_setup import logger


def get_nist_problem_files(search_dir):
    """
    """

    nist_lower = ['Misra1a.dat', 'Chwirut2.dat', 'Chwirut1.dat', 'Lanczos3.dat',
                  'Gauss1.dat', 'Gauss2.dat', 'DanWood.dat', 'Misra1b.dat']
    nist_average = ['Kirby2.dat', 'Hahn1.dat', 'MGH17.dat', 'Lanczos1.dat',
                    'Lanczos2.dat', 'Gauss3.dat', 'Misra1c.dat', 'Misra1d.dat',
                    'ENSO.dat']
    nist_higher = ['MGH09.dat', 'Thurber.dat', 'BoxBOD.dat', 'Rat42.dat',
                   'MGH10.dat', 'Eckerle4.dat', 'Rat43.dat', 'Bennett5.dat']

    nist_lower = [os.path.join(search_dir, fname) for fname in nist_lower]
    nist_average = [os.path.join(search_dir, fname) for fname in nist_average]
    nist_higher = [os.path.join(search_dir, fname) for fname in nist_higher]
    problem_files = [nist_lower_files, nist_average_files, nist_higher_files]

    return problem_files


def get_neutron_problem_files(search_dir):
    """
    """

    search_str = os.path.join(search_dir, "*.txt")
    probs = glob.glob(search_str)
    probs.sort()

    for problem in probs:
        logger.info(problem)

    return [probs]
