from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from resproc.numpy_restables import create_accuracy_runtime_tbls
from resproc.numpy_restables import create_norm_tbls
from resproc.numpy_restables import create_summary_tbls
from utils import fitbm_result

class NumpyRestablesTests(unittest.TestCase):

    def results_per_test_setup(self):

        chi_sq = np.array([[2, 4, 6],
                           [4, 6, 8],])
        runtime = np.array([[2, 4, 6],
                            [4, 6, 8]])

        results_per_test = []
        for test_idx in range(0, len(chi_sq)):
            prob_results = []
            for minimiz_idx in range(0, len(chi_sq[test_idx])):
                result = fitbm_result.FittingResult()
                result.chi_sq = chi_sq[test_idx][minimiz_idx]
                result.runtime = runtime[test_idx][minimiz_idx]
                prob_results.append(result)
            results_per_test.append(prob_results)

        return results_per_test


    def accuracy_and_runtime_mock_tables(self):

        accuracy_tbl = np.array([[1,2,3],
                                 [20,4,720]])
        time_tbl = np.array([[1,2,3],
                             [20,4,720]])

        return accuracy_tbl, time_tbl


    def expected_normalised_mock_tables(self):

        norm_acc_rankings = np.array([[1,2,3],
                                      [5,1,180]])
        norm_runtimes = np.array([[1,2,3],
                                  [5,1,180]])

        return norm_acc_rankings, norm_runtimes


    def expected_summary_mock_tables(self):

        summary_cells_acc = np.array([[1,1,3],
                                      [5,2,180],
                                      [3,1.5,91.5],
                                      [3,1.5,91.5]])
        summary_cells_runtime = np.array([[1,1,3],
                                          [5,2,180],
                                          [3,1.5,91.5],
                                          [3,1.5,91.5]])

        return summary_cells_acc, summary_cells_runtime


    def test_createAccuracyRuntimeTbls_return_accuracy_and_runtime_tables(self):

        results_per_test = self.results_per_test_setup()
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        accuracy_tbl, time_tbl = \
        create_accuracy_runtime_tbls(results_per_test, minimizers)
        accuracy_tbl_expected = np.array([[2, 4, 6],
                                          [4, 6, 8]])
        time_tbl_expected = np.array([[2, 4, 6],
                                      [4, 6, 8]])

        np.testing.assert_array_equal(accuracy_tbl_expected, accuracy_tbl)
        np.testing.assert_array_equal(time_tbl_expected, time_tbl)


    def test_createNormTables_return_normalised_tables_given_mock_tables(self):

        accuracy_tbl, time_tbl = self.accuracy_and_runtime_mock_tables()

        norm_acc_rankings, norm_runtimes = \
        create_norm_tbls(accuracy_tbl, time_tbl)
        norm_acc_rankings_expected, norm_runtimes_expected = \
        self.expected_normalised_mock_tables()

        np.testing.assert_array_equal(norm_acc_rankings_expected,
                                      norm_acc_rankings)
        np.testing.assert_array_equal(norm_runtimes_expected, norm_runtimes)


    def test_createSummaryTbls_return_normalised_tables_given_mock_tables(self):

        norm_acc_rankings, norm_runtimes = \
        self.expected_normalised_mock_tables()

        summary_cells_acc, summary_cells_runtime = \
        create_summary_tbls(norm_acc_rankings, norm_runtimes)
        summary_cells_acc_expected, summary_cells_runtime_expected = \
        self.expected_summary_mock_tables()

        np.testing.assert_array_equal(summary_cells_acc_expected,
                                      summary_cells_acc)
        np.testing.assert_array_equal(summary_cells_runtime_expected,
                                      summary_cells_runtime)


if __name__ == "__main__":
    unittest.main()

