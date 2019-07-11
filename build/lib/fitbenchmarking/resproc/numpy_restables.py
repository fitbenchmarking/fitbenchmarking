"""
Functions that create numpy arrays of the accuracy and runtime obtained
through fitting a set of problems by using various minimizers and a
certain fitting software.
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
import numpy as np

# Older version of numpy does not support nanmean and nanmedian
# and nanmean and nanmedian was removed in scipy 0.18 in favor of numpy
# so try numpy first then scipy.stats
try:
    from numpy import nanmean, nanmedian
except ImportError:
    from scipy.stats import nanmean, nanmedian


def create_accuracy_runtime_tbls(results_per_test, minimizers):
    """
    Creates numpy tables of the accuracy and the runtime.

    @param results_per_test :: object that holds the results of the fitting
    @param minimizers :: array of strings containing minimizer names

    @returns :: numpy arrays of the results
    """

    accuracy_tbl, time_tbl = init_numpy_tbls(results_per_test, minimizers)
    for test_idx in range(0, len(results_per_test)):
        for minimiz_idx in range(0, len(minimizers)):
            accuracy_tbl[test_idx, minimiz_idx] = \
                results_per_test[test_idx][minimiz_idx].chi_sq

            time_tbl[test_idx, minimiz_idx] = \
                results_per_test[test_idx][minimiz_idx].runtime

    return accuracy_tbl, time_tbl


def create_norm_tbls(accuracy_tbl, time_tbl):
    """
    Normalises the results per problem with respect to the lowest one.

    @param accuracy_tbl :: numpy array of the obtained chis
    @param time_tbl :: numpy array of the obtained runtimes

    @returns :: numpy arrays of normalised accuracy and runtime tables
    """

    min_chi_sq = np.nanmin(accuracy_tbl, 1)
    min_runtime = np.nanmin(time_tbl, 1)

    # Create normalised numpy tables
    norm_acc_rankings = accuracy_tbl / min_chi_sq[:, None]
    norm_runtimes = time_tbl / min_runtime[:, None]

    return norm_acc_rankings, norm_runtimes,


def create_summary_tbls(norm_acc_rankings, norm_runtimes):
    """
    Creates summary tables of the obtained results, i.e. the minimum
    maximum, mean and median of each column in the normalised numpy
    arrays.

    @param norm_acc_rankings :: the normalised accuracy results numpy array
    @param norm_runtimes :: the normalised runtime results numpy array

    @returns :: the summary tables for both runtime and accuracy
    """

    summary_cells_acc = np.array([np.nanmin(norm_acc_rankings, 0),
                                  np.nanmax(norm_acc_rankings, 0),
                                  nanmean(norm_acc_rankings, 0),
                                  nanmedian(norm_acc_rankings, 0)])

    summary_cells_runtime = np.array([np.nanmin(norm_runtimes, 0),
                                      np.nanmax(norm_runtimes, 0),
                                      nanmean(norm_runtimes, 0),
                                      nanmedian(norm_runtimes, 0)])

    return summary_cells_acc, summary_cells_runtime


def init_numpy_tbls(results_per_test, minimizers):
    """
    Helper function that initialises the numpy tables.

    @param results_per_test :: object that holds the results of the fitting
    @param minimizers :: array of strings containing minimizer names

    @returns :: accuracy and runtime numpy arrays filled with zeros
    """

    num_tests = len(results_per_test)
    num_minimizers = len(minimizers)

    accuracy_tbl = np.zeros((num_tests, num_minimizers))
    time_tbl = np.zeros((num_tests, num_minimizers))

    return accuracy_tbl, time_tbl
