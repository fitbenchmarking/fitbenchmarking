"""
Functions that create numpy arrays of the accuracy and runtime obtained
through fitting a set of problems by using various minimizers and a
certain fitting software.
"""

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


def create_summary_tbls(acc_rankings, runtimes):
    """
    Creates summary tables of the obtained results, i.e. the minimum
    maximum, mean and median of each column in the normalised numpy
    arrays.

    @param acc_rankings :: the combined accuracy results numpy array
    @param runtimes :: the combined runtime results numpy array

    @returns :: the summary tables for both runtime and accuracy
    """
    acc_rankings = acc_rankings[:, :, 1]
    runtimes = runtimes[:, :, 1]

    summary_cells_acc = np.array([np.nanmin(acc_rankings, 0),
                                  np.nanmax(acc_rankings, 0),
                                  nanmean(acc_rankings, 0),
                                  nanmedian(acc_rankings, 0)])

    summary_cells_runtime = np.array([np.nanmin(runtimes, 0),
                                      np.nanmax(runtimes, 0),
                                      nanmean(runtimes, 0),
                                      nanmedian(runtimes, 0)])

    return summary_cells_acc, summary_cells_runtime


def create_combined_tbls(abs_accuracy, rel_accuracy, abs_runtime, rel_runtime):
    """
    Create a table that holds both absolute and relative information on
    each result.

    @param abs_accuracy :: The table with the absolute accuracy reported
    @param rel_accuracy :: The table with the relative accuracy reported
    @param abs_runtime :: The table with the absolute runtime reported
    @param rel_runtime :: The table with the relative runtime reported

    @returns :: combined_accuracy and combined_runtime tables with both
                values present in each cell.
                e.g. combined_accuracy[2,3,0] == rel_accuracy[2,3]
                     combined_accuracy[2,3,1] == abs_accuracy[2,3]
    """

    accuracy_shape = (abs_accuracy.shape[0], abs_accuracy.shape[1], 2)
    runtime_shape = (abs_runtime.shape[0], abs_runtime.shape[1], 2)

    combined_accuracy = np.zeros(accuracy_shape)
    combined_runtime = np.zeros(runtime_shape)

    combined_accuracy[:, :, 0] = abs_accuracy
    combined_accuracy[:, :, 1] = rel_accuracy

    combined_runtime[:, :, 0] = abs_runtime
    combined_runtime[:, :, 1] = rel_runtime

    return combined_accuracy, combined_runtime


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
