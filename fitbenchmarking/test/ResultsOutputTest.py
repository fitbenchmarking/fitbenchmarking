from __future__ import (absolute_import, division, print_function)

import unittest
import os
import mantid.simpleapi as msapi
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from results_output import build_indiv_linked_problems
from results_output import build_visual_display_page
from results_output import build_rst_table
from results_output import build_items_links
from results_output import display_name_for_minimizers
from results_output import calc_cell_len_rst_table
from results_output import calc_first_col_len
from results_output import build_rst_table_header_chunks
from results_output import format_cell_value_rst
from results_output import weighted_suffix_string
from results_output import save_table_to_file
from post_processing import calc_accuracy_runtime_tbls
from post_processing import calc_norm_summary_tables
import test_result
import test_problem


class ResultsOutputTests(unittest.TestCase):

    def DumpDir(self):
        """
        Path to a directory where file output of various functions
        is dumped.
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        dump_dir = os.path.join(current_dir, 'dump')

        return dump_dir


    def NISTproblem(self):
        """ Sets up the problem object for the nist problem file Misra1a.dat """

        data_pattern = np.array([ [10.07, 77.6],
                                  [14.73, 114.9],
                                  [17.94, 141.1],
                                  [23.93, 190.8],
                                  [29.61, 239.9],
                                  [35.18, 289.0],
                                  [40.02, 332.8],
                                  [44.82, 378.4],
                                  [50.76, 434.8],
                                  [55.05, 477.3],
                                  [61.01, 536.8],
                                  [66.40, 593.1],
                                  [75.47, 689.1],
                                  [81.78, 760.0] ])

        prob = test_problem.FittingTestProblem()
        prob.name = 'Misra1a'
        prob.linked_name = ("`Misra1a <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/misra1a.shtml>`__")
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894E-01

        return prob


    def ExpectedResultObjectNISTproblemMisra1a(self):

        prob = self.NISTproblem()

        result1 = test_result.FittingTestResult()
        result1.problem = prob
        result1.fit_status = 'success'
        result1.chi_sq = 0.153327111
        result1.params = [234.53440075754118, 0.00056218017032756289]
        result1.errors = [166.95843730560517, 0.00045840028643556361]
        result1.minimizer = 'Levenberg-Marquardt'
        result1.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=500.0,b2=0.0001,")

        result2 = test_result.FittingTestResult()
        result2.problem = prob
        result2.fit_status = 'success'
        result2.chi_sq = 0.153326918
        result2.params = [234.53441741161569, 0.00056218011624728884]
        result2.errors = [166.95846246387609, 0.00045840028235511008]
        result2.minimizer = 'Levenberg-Marquardt'
        result2.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=250.0,b2=0.0005,")

        return [result1], [result2]


    def SetupNISTResults(self):
        ''' Sets up the results object with only the needed attributes for
            the problems in the names array '''

        results_per_test = self.ExpectedResultObjectNISTproblemMisra1a()

        return results_per_test


    def AccuracyAndRuntimeMockTables(self):

        accuracy_tbl = np.array([[1,2,3],
                                 [20,4,720]])
        time_tbl = np.array([[1,2,3],
                             [20,4,720]])

        return accuracy_tbl, time_tbl


    def ExpectedNormalisedMockTables(self):

        norm_acc_rankings = np.array([[1,2,3],
                                      [5,1,180]])
        norm_runtimes = np.array([[1,2,3],
                                  [5,1,180]])
        summary_cells_acc = np.array([[1,1,3],
                                      [5,2,180],
                                      [3,1.5,91.5],
                                      [3,1.5,91.5]])
        summary_cells_runtime = np.array([[1,1,3],
                                          [5,2,180],
                                          [3,1.5,91.5],
                                          [3,1.5,91.5]])

        return (norm_acc_rankings, norm_runtimes, summary_cells_acc,
                summary_cells_runtime)


    def TablesSetup(self):
        ''' Helper function that sets up the group_results
            accuracy and runtime tables tables '''

        chi_sq = np.array([[2, 4, 6],
                           [4, 6, 8],])
        runtime = np.array([[2, 4, 6],
                            [4, 6, 8]])

        group_results = []
        for group_idx in range(0,3):
            results_per_test = []

            for test_idx in range(0, len(chi_sq)):
                prob_results = []
                for minimiz_idx in range(0, len(chi_sq[test_idx])):
                    result = test_result.FittingTestResult()
                    result.chi_sq = chi_sq[test_idx][minimiz_idx]
                    result.runtime = runtime[test_idx][minimiz_idx]
                    prob_results.append(result)

                results_per_test.append(prob_results)

            group_results.append(results_per_test)
            chi_sq += 3
            runtime += 3

        return group_results


    def PrepareTableHeader(self):
        ''' Helper function that returns the headers used in making the rst table '''

        tbl_header_top = ("+" + "-"*105 + "+" + ("-"*21 + "+")*10)
        tbl_header_text = ("|" + " "*105 + "|" + "Minimizer1" + " "*11 + "|" + \
                           "Minimizer2" + 11*" " + "|" + "Minimizer3" + " "*11 +
                           "|" + \
                           "Minimizer4" + 11*" " + "|" + "Minimizer5" + " "*11 +
                           "|" + \
                           "Minimizer6" + 11*" " + "|" + "Minimizer7" + " "*11 +
                           "|" + \
                           "Minimizer8" + 11*" " + "|" + "Minimizer9" + " "*11 +
                           "|" + \
                           "Trust Region" + " "*9 + "|")
        tbl_header_bottom = ("+" + "="*105 + "+" + ("="*21 + "+")*10)

        return tbl_header_top, tbl_header_text, tbl_header_bottom


    def GenerateRstTable(self):
        ''' Helper function that generates the rst tables for comparison '''

        tbl_header_top, tbl_header_text, tbl_header_bottom = self.PrepareTableHeader()
        tbl_header = tbl_header_top + '\n' + tbl_header_text + '\n' + \
                     tbl_header_bottom + '\n'
        tbl_footer = tbl_header_top + '\n'
        tbl_body = ("|`Misra1a 1 <file:///d:/fitbenchmarking/fitbenchmarking/" +
                    "test/dump/nist/VDPages/nist_lower_misra1a.html>`__|" +
                    " :ranking-top-1:`1`  | :ranking-low-4:`2`  | " +
                    ":ranking-low-4:`3`  |\n"
                    + tbl_footer +
                    "|`Misra1a 2 <file:///d:/fitbenchmarking/fitbenchmarking/" +
                    "test/dump/nist/VDPages/nist_lower_misra1a.html>`__|" +
                    " :ranking-low-5:`5`  | :ranking-low-5:`10` |" +
                    " :ranking-low-5:`13` |\n"
                    + tbl_footer)
        tbl = tbl_header + tbl_body

        return tbl


    def PrepareBuildRSTTableFunctionParameters(self):

        minimizers = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4',
                      'Minimizer5', 'Minimizer6','Minimizer7','Minimizer8',
                      'Minimizer9','DTRS']
        linked_problems = ["`Misra1a 1 <file:///d:/fitbenchmarking/"
                           "fitbenchmarking/test/dump/nist/"
                           "VDPages/nist_lower_misra1a.html>`__",
                           "`Misra1a 2 <file:///d:/fitbenchmarking/"
                           "fitbenchmarking/test/dump/nist/"
                           "VDPages/nist_lower_misra1a.html>`__"]
        norm_acc_rankings = np.array([[1,2,3],
                                      [5,10,13]])
        use_errors = True
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]

        return minimizers, linked_problems, norm_acc_rankings, use_errors, color_scale


    def CalcCellLenRSTTableParameters(self):

        columns_txt = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4',
                       'Minimizer5', 'Minimizer6','Minimizer7','Minimizer8',
                       'Minimizer9', 'Trust Region']
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'
        cells = np.array([[1,2,3],
                          [5,10,13]])
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]

        return columns_txt, items_link, cells, color_scale


    def test_buildIndivLinkedProblems_return_NIST_files_Misra1a_linked_problems(self):

        dump_dir = self.DumpDir()
        results_per_test = self.SetupNISTResults()
        group_name = 'nist_lower'
        aux_dir = os.path.join(dump_dir, "nist", "VDPages")
        os.makedirs(aux_dir)

        linked_problems = \
        build_indiv_linked_problems(results_per_test, group_name, dump_dir)
        linked_problems_expected = ["`Misra1a 1 <file:///d:/fitbenchmarking/"
                                    "fitbenchmarking/test/dump/nist/"
                                    "VDPages/nist_lower_misra1a.html>`__",
                                    "`Misra1a 2 <file:///d:/fitbenchmarking/"
                                    "fitbenchmarking/test/dump/nist/"
                                    "VDPages/nist_lower_misra1a.html>`__"]

        self.assertListEqual(linked_problems_expected, linked_problems)


    def test_calcAccuracyRuntimeTbls_return_accuracy_and_runtime_tables(self):

        results_per_test = self.TablesSetup()[0]
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        accuracy_tbl, time_tbl = \
        calc_accuracy_runtime_tbls(results_per_test, minimizers)
        accuracy_tbl_expected = np.array([[2, 4, 6],
                                          [4, 6, 8]])
        time_tbl_expected = np.array([[2, 4, 6],
                                      [4, 6, 8]])

        np.testing.assert_array_equal(accuracy_tbl_expected, accuracy_tbl)
        np.testing.assert_array_equal(time_tbl_expected, time_tbl)


    def test_calcNormSummaryTables_return_normalised_tables_given_mock_tables(self):

        accuracy_tbl, time_tbl = self.AccuracyAndRuntimeMockTables()

        (norm_acc_rankings, norm_runtimes,
         summary_cells_acc, summary_cells_runtime) = \
        calc_norm_summary_tables(accuracy_tbl, time_tbl)
        (norm_acc_rankings_expected,
         norm_runtimes_expected,
         summary_cells_acc_expected,
         summary_cells_runtime_expected) = self.ExpectedNormalisedMockTables()

        np.testing.assert_array_equal(norm_acc_rankings_expected,
                                      norm_acc_rankings)
        np.testing.assert_array_equal(norm_runtimes_expected, norm_runtimes)
        np.testing.assert_array_equal(summary_cells_acc_expected,
                                      summary_cells_acc)
        np.testing.assert_array_equal(summary_cells_runtime_expected,
                                      summary_cells_runtime)


    def test_buildRSTTable_return_rst_table_for_problem_files_Misra1a_Lanczos3_mock_minimizers(self):

        (minimizers, linked_problems, norm_acc_rankings,
         use_errors, color_scale) = \
        self.PrepareBuildRSTTableFunctionParameters()

        tbl = build_rst_table(minimizers, linked_problems, norm_acc_rankings,
                              comparison_type='accuracy', comparison_dim='',
                              using_errors=use_errors, color_scale=color_scale)
        tbl_expected = self.GenerateRstTable()

        self.assertEqual(tbl_expected, tbl)


    def test_displayNameForMinimizers_return_minimizer_mock_names(self):

        names = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4',
                 'Minimizer5', 'Minimizer6','Minimizer7','Minimizer8',
                 'Minimizer9','DTRS']

        display_names = display_name_for_minimizers(names)
        display_names_expected = ['Minimizer1','Minimizer2','Minimizer3',
                                  'Minimizer4','Minimizer5',
                                  'Minimizer6','Minimizer7','Minimizer8',
                                  'Minimizer9','Trust Region']

        self.assertListEqual(display_names_expected, display_names)


    def test_buildItemsLinks_return_summary_links(self):

        comparison_type = 'summary'
        comparison_dim = 'accuracy'
        using_errors = True

        items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = ['Minimizers_weighted_comparison_in_terms_of'
                               '_accuracy_nist_lower',
                               'Minimizers_weighted_comparison_in_terms_of'
                               '_accuracy_nist_average',
                               'Minimizers_weighted_comparison_in_terms_of'
                               '_accuracy_nist_higher',
                               'Minimizers_weighted_comparison_in_terms_of'
                               '_accuracy_cutest',
                               'Minimizers_weighted_comparison_in_terms_of'
                               '_accuracy_neutron_data']

        self.assertListEqual(items_link_expected, items_link)


    def test_buildItemsLinks_return_accuracy_links(self):

        comparison_type = 'accuracy'
        comparison_dim = ''
        using_errors = True

        items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = 'FittingMinimizersComparisonDetailedWithWeights'

        self.assertEqual(items_link_expected, items_link)


    def test_buildItemsLinks_return_runtime_links(self):

        comparison_type = 'runtime'
        comparison_dim = ''
        using_errors = False

        items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = 'FittingMinimizersComparisonDetailed'

        self.assertEqual(items_link_expected, items_link)


    def test_buildItemsLinks_return_empty_itemsLinks_invalid_comparison_type(self):

        comparison_type = 'pasta'
        comparison_dim = ''
        using_errors = False

        items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = ''

        self.assertEqual(items_link_expected, items_link)


    def test_weightedSuffixString_return_string_value_weighted(self):

        value = weighted_suffix_string(True)
        self.assertEqual(value, 'weighted')


    def test_weightedSuffixString_return_string_value_unweighted(self):

        value = weighted_suffix_string(False)
        self.assertEqual(value, 'unweighted')


    def test_calcCellLenRSTTable_cell_len_smaller_than_max_header_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = \
        self.CalcCellLenRSTTableParameters()

        cell_len = \
        calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 21

        self.assertEqual(cell_len_expected, cell_len)


    def test_calcCellLenRSTTable_cell_len_larger_than_max_header_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = \
        self.CalcCellLenRSTTableParameters()
        columns_txt = ['Alabalaportocala11345678']

        cell_len = calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 24

        self.assertEqual(cell_len_expected, cell_len)


    def test_FormatCellValueRST_no_color_scale_and_no_items_link_return_value_text(self):

        value_text = format_cell_value_rst(value=180, color_scale=0,
                                           items_link=0)
        self.assertEqual(' 180', value_text)


    def test_FormatCellValueRST_no_color_scale_return_value_text(self):

        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=180, color_scale=0,
                                           items_link=items_link)
        value_text_expected = \
        ' :ref:`180 <FittingMinimizersComparisonDetailedWithWeights>`'

        self.assertEqual(value_text_expected, value_text)


    def test_FormatCellValueRST_all_options_no_width_return_value_text(self):

        value = 2
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=value, color_scale=color_scale,
                                           items_link=items_link)
        value_text_expected = " :ranking-low-4:`2`"

        self.assertEqual(value_text_expected, value_text)


    def test_FormatCellValueRST_all_options_with_width_return_value_text(self):

        value = 180
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=value, width=25,
                                           color_scale=color_scale,
                                           items_link=items_link)
        value_text_expected = " :ranking-low-5:`180`    "

        self.assertEqual(value_text_expected, value_text)


    def test_calcFirstColLen_for_NIST_problem_Misra1a_and_Lanczos3(self):

        cell_len = 21
        rows_txt = ["`Misra1a 1 <file:///d:/fitbenchmarking/"
                    "fitbenchmarking/test/dump/nist/"
                    "VDPages/nist_lower_misra1a.html>`__",
                    "`Misra1a 2 <file:///d:/fitbenchmarking/"
                    "fitbenchmarking/test/dump/nist/"
                    "VDPages/nist_lower_misra1a.html>`__"]

        first_col_len = calc_first_col_len(cell_len, rows_txt)
        first_col_len_expected = 105

        self.assertEqual(first_col_len_expected, first_col_len)


    def test_buildRSTTableHeaderChunks_return_header_chucks_for_Misra1a_problem_results(self):

        first_col_len = 105
        cell_len = 21
        columns_txt = ['Minimizer1', 'Minimizer2', 'Minimizer3', 'Minimizer4',
                       'Minimizer5', 'Minimizer6', 'Minimizer7', 'Minimizer8',
                       'Minimizer9', 'Trust Region']

        (tbl_header_top, tbl_header_text,
         tbl_header_bottom) = build_rst_table_header_chunks(first_col_len,
                                                            cell_len,
                                                            columns_txt)
        (tbl_header_top_expected, tbl_header_text_expected,
         tbl_header_bottom_expected) = self.PrepareTableHeader()

        self.assertEqual(tbl_header_top_expected, tbl_header_top)
        self.assertEqual(tbl_header_text_expected, tbl_header_text)
        self.assertEqual(tbl_header_bottom_expected, tbl_header_bottom)


if __name__ == "__main__":
    unittest.main()
