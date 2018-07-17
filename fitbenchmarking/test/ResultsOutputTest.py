from __future__ import (absolute_import, division, print_function)

import unittest
import os
import mantid.simpleapi as msapi
import numpy as np

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from results_output import build_indiv_linked_problems
from results_output import build_visual_display_page
from results_output import build_group_linked_names
from results_output import build_rst_table
from results_output import build_items_links
from results_output import display_name_for_minimizers
from results_output import calc_cell_len_rst_table
from results_output import calc_first_col_len
from results_output import build_rst_table_header_chunks
from results_output import format_cell_value_rst
from results_output import weighted_suffix_string
from post_processing import calc_accuracy_runtime_tbls
from post_processing import calc_norm_summary_tables
from post_processing import calc_summary_table
import test_result
import test_problem


class ResultsOutput(unittest.TestCase):

    def test_build_indiv_linked_problems(self):

        linked_problems_actual = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                  "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                  "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                  "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                  "`DanWood 1 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__",
                                  "`DanWood 2 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__" ]

        results_per_test = []
        result = test_result.FittingTestResult()
        prob = test_problem.FittingTestProblem()

        group_name = 'nist_lower'
        linked_problems = build_indiv_linked_problems(results_per_test, group_name)

        self.assertListEqual(linked_problems_actual, linked_problems)


        linked_problems_actual = []

        results_per_test = self.GenerateResultsPerTestNeutron()
        group_name = 'neutron'
        linked_problems = build_indiv_linked_problems(results_per_test, group_name)

        self.assertListEqual(linked_problems_actual, linked_problems)


    def test_build_group_linked_names(self)

        linked_names_actual = ["`NIST, "lower" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__",
                               "`NIST, "average" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__",
                               "`NIST, "higher" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__" ]

        group_names = ['NIST, "lower" difficulty', 'NIST, "average" difficulty',
                       'NIST, "higher" difficulty']
        linked_names = build_group_linked_names(group_names)

        self.assertListEqual(linked_names_actual, linked_names)


    def test_build_visual_display_page(self):

        rst_link_actual = '`<ENGINX193749_calibration_peak19.txt.html>`_'

        prob_results = self.GenerateResultsPerTestNeutron()[0]
        group_name = 'neutron'

        rst_link = build_visual_display_page(prob_results, group_name)

        self.assertEqual(rst_link_actual, rst_link)


    def test_calc_accuracy_runtime_tbls(self):

        accuracy_tbl_actual = [[0.159784541],[0.159784814],[1.54111E-08],
                               [1.54111E-08],[0.004341888],[0.004341886]]
        time_tbl_actual = [[],[],[],[],[],[]]

        results_per_test = self.GenerateResultsPerTestNIST()
        minimizers = ['Levenberg-Marquardt']

        accuracy_tbl, time_tbl = calc_accuracy_runtime_tbls(results_per_test, minimizers)

        # The time test (latter one) is very machine dependent
        self.assertListEqual(accuracy_tbl_actual, accuracy_tbl)
        self.assertListEqual(time_tbl_actual, time_tbl)


    def test_calc_norm_summary_tables(self):

        norm_acc_rankings_actual = np.array([[1,2,3,4,5,6,7,8,9,10],
                                             [21,42,53,64,55,36,27,4,39,720]/4,
                                             [21,31,3,41,51,61,71,81,91,110]/3,
                                             [100,2,3,4,5,6,7,8,9,10]/2])
        norm_runtimes_actual = np.array([[1,2,3,4,5,6,7,8,9,10],
                                         [21,42,53,64,55,36,27,4,39,720]/4,
                                         [21,31,3,35,51,63,72,81,93,111]/3,
                                         [100,2,3,4,5,6,7,8,9,10]/2])
        summary_cells_acc_actual = np.array([[1,1,1,2,2.5,3,3.5,1,4.5,5],
                                             [50,10.5,13.25,16,17,21,24,27,31,37],
                                             [],
                                             []])
        summary_cells_acc_actual = np.array([[1,1,1,2,2.5,3,3.5,1,4.5,5],
                                             [50,10.5,13.25,16,17,21,24,27,31,37],
                                             [],
                                             []])

        accuracy_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                                 [21,42,53,64,55,36,27,18,39,720],
                                 [11,21,31,41,51,61,71,81,19,110],
                                 [1,2,3,4,5,6,7,8,9,10]])
        time_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                             [21,42,53,64,55,36,27,18,39,610],
                             [11,21,31,41,51,61,71,81,19,110],
                             [100,2,3,4,5,6,7,8,9,10]])

        (norm_acc_rankings, norm_runtimes,
         summary_cells_acc, summary_cells_runtime) = calc_norm_summary_tables(accuracy_tbl, time_tbl)

        np.testing.assert_array_equal(norm_acc_rankings_actual, norm_acc_rankings)
        np.testing.assert_array_equal(norm_runtimes_actual, norm_runtimes)
        np.testing.assert_array_equal(summary_cells_acc_actual, summary_cells_acc)
        np.testing.assert_array_equal(summary_cells_runtime_actual, summary_cells_runtime)


    def test_calc_summary_table(self):

        group_results
        for i in range(0,9):
            for j in range(0,9):


        minimizers = ['Levenberg-Marquardt']







if __name__ == "__main__":
    unittest.main()
