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
from results_output import save_table_to_file
from post_processing import calc_accuracy_runtime_tbls
from post_processing import calc_norm_summary_tables
from post_processing import calc_summary_table
import test_result
import test_problem


class ResultsOutputTests(unittest.TestCase):

    def SetupNISTResults(self):
        ''' Sets up the results object with only the needed attributes for
            the problems in the names array '''

        results_per_test = []
        names = ['Misra1a.dat', 'Misra1a.dat', 'Lanczos3.dat', 'Lanczos3.dat',
                 'DanWood.dat', 'DanWood.dat']

        for idx in range(0, len(names)):
            result = test_result.FittingTestResult()
            prob = test_problem.FittingTestProblem()
            prob.name = names[idx]
            result.problem = prob
            results_per_test.append([result])

        return results_per_test


    def SetupNeutronResults(self):
        ''' Sets up the results object with only the needed attributes for
            the problem ENGINX193749_calibration_peak19.txt '''

        prob_results = []
        name = 'ENGINX193749_calibration_peak19.txt'
        fit_chi2 = [1,2,3,4,5,6,7,8,9,10]
        data_pattern_in = np.array([1,2,3,4,5,6,7,8,9,10])
        data_pattern_out = np.array([10,20,30,40,50,60,70,80,90,100])

        for idx in range(0, len(fit_chi2)):
            result = test_result.FittingTestResult()
            prob = test_problem.FittingTestProblem()
            prob.name = name
            prob.data_pattern_in = data_pattern_in
            prob.data_pattern_out = data_pattern_out
            result.problem = prob
            result.fit_chi2 = fit_chi2[idx]
            prob_results.append(result)

        return prob_results


    def AccuracyAndRuntimeMockTables(self):

        accuracy_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                                 [20,40,52,64,52,36,24,4,36,720],
                                 [21,30,3,36,51,63,72,81,93,111],
                                 [100,2,4,6,8,10,12,14,16,18]])
        time_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                             [20,40,52,64,52,36,24,4,36,720],
                             [21,30,3,36,51,63,72,81,93,111],
                             [100,2,4,6,8,10,12,14,16,18]])

        return accuracy_tbl, time_tbl


    def ExpectedNormalisedMockTables(self):

        norm_acc_rankings = np.array([[1,2,3,4,5,6,7,8,9,10],
                                      [5,10,13,16,13,9,6,1,9,180],
                                      [7,10,1,12,17,21,24,27,31,37],
                                      [50,1,2,3,4,5,6,7,8,9]])
        norm_runtimes = np.array([[1,2,3,4,5,6,7,8,9,10],
                                  [5,10,13,16,13,9,6,1,9,180],
                                  [7,10,1,12,17,21,24,27,31,37],
                                  [50,1,2,3,4,5,6,7,8,9]])
        summary_cells_acc = np.array([[1,1,1,3,4,5,6,1,8,9],
                                      [50,10,13,16,17,21,24,27,31,180],
                                      [15.75,5.75,4.75,8.75,9.75,10.25,10.75,10.75,14.25,59],
                                      [6,6,2.5,8,9,7.5,6.5,7.5,9,23.5]])
        summary_cells_runtime = np.array([[1,1,1,3,4,5,6,1,8,9],
                                          [50,10,13,16,17,21,24,27,31,180],
                                          [15.75,5.75,4.75,8.75,9.75,10.25,10.75,10.75,14.25,59],
                                          [6,6,2.5,8,9,7.5,6.5,7.5,9,23.5]])

        return norm_acc_rankings, norm_runtimes, summary_cells_acc, summary_cells_runtime


    def TablesSetup(self):
        ''' Helper function that sets up the group_results
            accuracy and runtime tables tables '''

        sum_err_sq = np.array([[2, 4, 6],
                               [4, 6, 8],
                               [8, 16, 24]])
        runtime = np.array([[2, 4, 6],
                            [4, 6, 8],
                            [8, 16, 24]])

        group_results = []
        for group_idx in range(0,3):
            results_per_test = []

            for test_idx in range(0, len(sum_err_sq)):
                prob_results = []
                for minimiz_idx in range(0, len(sum_err_sq[test_idx])):
                    result = test_result.FittingTestResult()
                    result.sum_err_sq = sum_err_sq[test_idx][minimiz_idx]
                    result.runtime = runtime[test_idx][minimiz_idx]
                    prob_results.append(result)

                results_per_test.append(prob_results)

            group_results.append(results_per_test)
            sum_err_sq += 3
            runtime += 3

        return group_results


    def PrepareTableHeader(self):
        ''' Helper function that returns the headers used in making the rst table '''

        tbl_header_top = ("+" + "-"*76 + "+" + ("-"*22 + "+")*10)
        tbl_header_text = ("|" + " "*76 + "|" + "Minimizer1            |" + \
                           "Minimizer2            |" + "Minimizer3            |" + \
                           "Minimizer4            |" + "Minimizer5            |" + \
                           "Minimizer6            |" + "Minimizer7            |" + \
                           "Minimizer8            |" + "Minimizer9            |" + \
                           "Trust Region          |")
        tbl_header_bottom = ("+" + "="*76 + "+" + ("="*22 + "+")*10)

        return tbl_header_top, tbl_header_text, tbl_header_bottom


    def GenerateRstTable(self):
        ''' Helper function that generates the rst tables for comparison '''

        tbl_header_top, tbl_header_text, tbl_header_bottom = self.PrepareTableHeader()
        tbl_header = tbl_header_top + '\n' + tbl_header_text + '\n' + tbl_header_bottom + '\n'
        tbl_footer = tbl_header_top + '\n'
        tbl_body = ("|`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__  |"
                    " :ranking-top-1:`1`   | :ranking-low-4:`2`   | :ranking-low-4:`3`   |"
                    " :ranking-low-5:`4`   | :ranking-low-5:`5`   | :ranking-low-5:`6`   |"
                    " :ranking-low-5:`7`   | :ranking-low-5:`8`   | :ranking-low-5:`9`   |"
                    " :ranking-low-5:`10`  |\n" + tbl_footer +
                    "|`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__  |"
                    " :ranking-low-5:`5`   | :ranking-low-5:`10`  | :ranking-low-5:`13`  |"
                    " :ranking-low-5:`16`  | :ranking-low-5:`13`  | :ranking-low-5:`9`   |"
                    " :ranking-low-5:`6`   | :ranking-top-1:`1`   | :ranking-low-5:`9`   |"
                    " :ranking-low-5:`180` |\n" + tbl_footer +
                    "|`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__|"
                    " :ranking-low-5:`7`   | :ranking-low-5:`10`  | :ranking-top-1:`1`   |"
                    " :ranking-low-5:`12`  | :ranking-low-5:`17`  | :ranking-low-5:`21`  |"
                    " :ranking-low-5:`24`  | :ranking-low-5:`27`  | :ranking-low-5:`31`  |"
                    " :ranking-low-5:`37`  |\n" + tbl_footer +
                    "|`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__|"
                    " :ranking-low-5:`50`  | :ranking-top-1:`1`   | :ranking-low-4:`2`   |"
                    " :ranking-low-4:`3`   | :ranking-low-5:`4`   | :ranking-low-5:`5`   |"
                    " :ranking-low-5:`6`   | :ranking-low-5:`7`   | :ranking-low-5:`8`   |"
                    " :ranking-low-5:`9`   |\n" + tbl_footer)
        tbl = tbl_header + tbl_body

        return tbl


    def PrepareBuildRSTTableFunctionParameters(self):

        minimizers = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                      'Minimizer6','Minimizer7','Minimizer8','Minimizer9','DTRS']
        linked_problems = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                           "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                           "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                           "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__"]
        norm_acc_rankings = np.array([[1,2,3,4,5,6,7,8,9,10],
                                      [5,10,13,16,13,9,6,1,9,180],
                                      [7,10,1,12,17,21,24,27,31,37],
                                      [50,1,2,3,4,5,6,7,8,9]])
        use_errors = True
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]

        return minimizers, linked_problems, norm_acc_rankings, use_errors, color_scale


    def CalcCellLenRSTTableParameters(self):

        columns_txt = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                       'Minimizer6','Minimizer7','Minimizer8','Minimizer9','Trust Region']
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'
        cells = np.array([[1,2,3,4,5,6,7,8,9,10],
                          [5,10,13,16,13,9,6,1,9,180],
                          [7,10,1,12,17,21,24,27,31,37],
                          [50,1,2,3,4,5,6,7,8,9]])
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]

        return columns_txt, items_link, cells, color_scale


    def test_buildIndivLinkedProblems_return_NIST_files_Misra1a_Lanczos3_DanWood_linked_problems(self):

        results_per_test = self.SetupNISTResults()
        group_name = 'nist_lower'

        linked_problems = build_indiv_linked_problems(results_per_test, group_name)
        linked_problems_expected = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                    "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                    "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                    "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                    "`DanWood 1 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__",
                                    "`DanWood 2 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__" ]

        self.assertListEqual(linked_problems_expected, linked_problems)


    def test_buildIndivLinkedProblems_return_neutron_file_ENGINXpeak19_linked_problem(self):

        result = self.SetupNeutronResults()
        results_per_test = [result]
        group_name = 'neutron'

        linked_problems = build_indiv_linked_problems(results_per_test, group_name)
        linked_problems_expected = ["ENGINX193749_calibration_peak19"
                                    " `<neutron_enginx193749_calibration_peak19.txt.html>`_"]

        self.assertListEqual(linked_problems_expected, linked_problems)


    def test_buildGroupLinkedNames_return_NIST_group_linked_names(self):

        group_names = ['NIST, "lower" difficulty', 'NIST, "average" difficulty',
                       'NIST, "higher" difficulty']

        linked_names = build_group_linked_names(group_names)
        linked_names_expected = ['`NIST, "lower" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__',
                                 '`NIST, "average" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__',
                                 '`NIST, "higher" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__' ]

        self.assertListEqual(linked_names_expected, linked_names)


    def test_buildVisualDisplayPage_return_ENGINXpeak19_rst_visual_display_page(self):

        prob_results = self.SetupNeutronResults()
        group_name = 'neutron'

        rst_link = build_visual_display_page(prob_results, group_name)
        rst_link_expected = '`<neutron_enginx193749_calibration_peak19.txt.html>`_'

        self.assertEqual(rst_link_expected, rst_link)


    def test_calcNormSummaryTables_return_normalised_tables_given_mock_tables(self):

        accuracy_tbl, time_tbl = self.AccuracyAndRuntimeMockTables()

        (norm_acc_rankings, norm_runtimes,
         summary_cells_acc, summary_cells_runtime) = calc_norm_summary_tables(accuracy_tbl, time_tbl)
        (norm_acc_rankings_expected,
         norm_runtimes_expected,
         summary_cells_acc_expected,
         summary_cells_runtime_expected) = self.ExpectedNormalisedMockTables()


        np.testing.assert_array_equal(norm_acc_rankings_expected, norm_acc_rankings)
        np.testing.assert_array_equal(norm_runtimes_expected, norm_runtimes)
        np.testing.assert_array_equal(summary_cells_acc_expected, summary_cells_acc)
        np.testing.assert_array_equal(summary_cells_runtime_expected, summary_cells_runtime)


    def test_calcAccuracyRuntimeTbls_return_accuracy_and_runtime_tables(self):

        results_per_test = self.TablesSetup()[0]
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        accuracy_tbl, time_tbl = calc_accuracy_runtime_tbls(results_per_test, minimizers)
        accuracy_tbl_expected = np.array([[2, 4, 6],
                                          [4, 6, 8],
                                          [8, 16, 24]])
        time_tbl_expected = np.array([[2, 4, 6],
                                      [4, 6, 8],
                                      [8, 16, 24]])

        np.testing.assert_array_equal(accuracy_tbl_expected, accuracy_tbl)
        np.testing.assert_array_equal(time_tbl_expected, time_tbl)


    def test_calcSummaryTable_return_mock_summary_tables_using_TablesSetup_input(self):

        group_results = self.TablesSetup()
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        groups_norm_acc, groups_norm_runtime = calc_summary_table(minimizers, group_results)
        groups_norm_acc_expected = np.array([[1,2,3],[1,1.4,1.8],[1,1.25,1.5]])
        groups_norm_runtime_expected = np.array([[1,2,3],[1,1.4,1.8],[1,1.25,1.5]])

        np.testing.assert_array_equal(groups_norm_acc_expected, groups_norm_acc)
        np.testing.assert_array_equal(groups_norm_runtime_expected, groups_norm_runtime)


    def test_buildRSTTable_return_rst_table_for_problem_files_Misra1a_Lanczos3_mock_minimizers(self):

        (minimizers, linked_problems, norm_acc_rankings,
         use_errors, color_scale) = self.PrepareBuildRSTTableFunctionParameters()

        tbl = build_rst_table(minimizers, linked_problems, norm_acc_rankings,
                              comparison_type='accuracy', comparison_dim='',
                              using_errors=use_errors, color_scale=color_scale)
        tbl_expected = self.GenerateRstTable()

        self.assertEqual(tbl_expected, tbl)


    def test_displayNameForMinimizers_return_minimizer_mock_names(self):

        names = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                 'Minimizer6','Minimizer7','Minimizer8','Minimizer9','DTRS']

        display_names = display_name_for_minimizers(names)
        display_names_expected = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                                  'Minimizer6','Minimizer7','Minimizer8','Minimizer9','Trust Region']

        self.assertListEqual(display_names_expected, display_names)


    def test_buildItemsLinks_return_summary_links(self):

        comparison_type = 'summary'
        comparison_dim = 'accuracy'
        using_errors = True

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = ['Minimizers_weighted_comparison_in_terms_of_accuracy_nist_lower',
                               'Minimizers_weighted_comparison_in_terms_of_accuracy_nist_average',
                               'Minimizers_weighted_comparison_in_terms_of_accuracy_nist_higher',
                               'Minimizers_weighted_comparison_in_terms_of_accuracy_cutest',
                               'Minimizers_weighted_comparison_in_terms_of_accuracy_neutron_data']

        self.assertListEqual(items_link_expected, items_link)


    def test_buildItemsLinks_return_accuracy_links(self):

        comparison_type = 'accuracy'
        comparison_dim = ''
        using_errors = True

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = 'FittingMinimizersComparisonDetailedWithWeights'

        self.assertEqual(items_link_expected, items_link)

    def test_buildItemsLinks_return_runtime_links(self):

        comparison_type = 'runtime'
        comparison_dim = ''
        using_errors = False

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = 'FittingMinimizersComparisonDetailed'

        self.assertEqual(items_link_expected, items_link)


    def test_buildItemsLinks_return_empty_itemsLinks_invalid_comparison_type(self):

        comparison_type = 'pasta'
        comparison_dim = ''
        using_errors = False

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)
        items_link_expected = ''

        self.assertEqual(items_link_expected, items_link)


    def test_weightedSuffixString_return_string_value_weighted(self):

        value = weighted_suffix_string(True)
        self.assertEqual(value, 'weighted')


    def test_weightedSuffixString_return_string_value_unweighted(self):

        value = weighted_suffix_string(False)
        self.assertEqual(value, 'unweighted')


    def test_calcCellLenRSTTable_cell_len_smaller_than_max_header_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = self.CalcCellLenRSTTableParameters()

        cell_len = calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 22

        self.assertEqual(cell_len_expected, cell_len)


    def test_calcCellLenRSTTable_cell_len_larger_than_max_header_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = self.CalcCellLenRSTTableParameters()
        columns_txt = ['Alabalaportocala12345678']

        cell_len = calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 24

        self.assertEqual(cell_len_expected, cell_len)


    def test_FormatCellValueRST_no_color_scale_and_no_items_link_return_value_text(self):

        value_text = format_cell_value_rst(value=180, color_scale=0, items_link=0)
        self.assertEqual(' 180', value_text)


    def test_FormatCellValueRST_no_color_scale_return_value_text(self):

        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=180, color_scale=0,
                                           items_link=items_link)
        value_text_expected = ' :ref:`180 <FittingMinimizersComparisonDetailedWithWeights>`'

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

        cell_len = 22
        rows_txt = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                    "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                    "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                    "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__"]

        first_col_len = calc_first_col_len(cell_len, rows_txt)
        first_col_len_expected = 76

        self.assertEqual(first_col_len_expected, first_col_len)


    def test_buildRSTTableHeaderChunks_return_header_chucks_for_Misra1a_and_Lanczos3_problem_results(self):

        first_col_len = 76
        cell_len = 22
        columns_txt = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                       'Minimizer6','Minimizer7','Minimizer8','Minimizer9','Trust Region']

        (tbl_header_top, tbl_header_text,
         tbl_header_bottom) = build_rst_table_header_chunks(first_col_len,
                                                            cell_len,
                                                            columns_txt)
        (tbl_header_top_expected, tbl_header_text_expected,
         tbl_header_bottom_expected) = self.PrepareTableHeader()

        self.assertEqual(tbl_header_top_expected, tbl_header_top)
        self.assertEqual(tbl_header_text_expected, tbl_header_text)
        self.assertEqual(tbl_header_bottom_expected, tbl_header_bottom)


    def test_saveTableToFile_check_if_nist_files_are_created(self):

        tbl_acc_indiv = self.GenerateRstTable()

        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='acc', file_extension='txt')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='acc', file_extension='html')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='runtime', file_extension='txt')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='runtime', file_extension='html')
        file_name_expected1 = "comparison_weighted_v3.8_acc_nist.txt"
        file_name_expected2 = "comparison_weighted_v3.8_acc_nist.html"
        file_name_expected3 = "comparison_weighted_v3.8_runtime_nist.txt"
        file_name_expected4 = "comparison_weighted_v3.8_runtime_nist.html"

        self.assertTrue(os.path.isfile(file_name_expected1))
        self.assertTrue(os.path.isfile(file_name_expected2))
        self.assertTrue(os.path.isfile(file_name_expected3))
        self.assertTrue(os.path.isfile(file_name_expected4))


if __name__ == "__main__":
    unittest.main()
