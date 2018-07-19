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


class ResultsOutput(unittest.TestCase):

    def SetupNISTResults(self):

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


    def test_build_indiv_linked_problems(self):

        linked_problems_actual = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                  "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                                  "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                  "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                                  "`DanWood 1 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__",
                                  "`DanWood 2 <http://www.itl.nist.gov/div898/strd/nls/data/danwood.shtml>`__" ]

        results_per_test = self.SetupNISTResults()
        group_name = 'nist_lower'
        linked_problems = build_indiv_linked_problems(results_per_test, group_name)

        self.assertListEqual(linked_problems_actual, linked_problems)


        linked_problems_actual = ['ENGINX193749_calibration_peak19 `<neutron_enginx193749_calibration_peak19.txt.html>`_']

        result = self.SetupNeutronResults()
        results_per_test = [result]
        group_name = 'neutron'
        linked_problems = build_indiv_linked_problems(results_per_test, group_name)

        self.assertListEqual(linked_problems_actual, linked_problems)


    def test_build_group_linked_names(self):

        linked_names_actual = ['`NIST, "lower" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__',
                               '`NIST, "average" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__',
                               '`NIST, "higher" difficulty <http://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`__' ]

        group_names = ['NIST, "lower" difficulty', 'NIST, "average" difficulty',
                       'NIST, "higher" difficulty']
        linked_names = build_group_linked_names(group_names)

        self.assertListEqual(linked_names_actual, linked_names)


    def test_build_visual_display_page(self):

        rst_link_actual = '`<neutron_enginx193749_calibration_peak19.txt.html>`_'

        prob_results = self.SetupNeutronResults()
        group_name = 'neutron'

        rst_link = build_visual_display_page(prob_results, group_name)

        self.assertEqual(rst_link_actual, rst_link)


    def test_calc_norm_summary_tables(self):

        norm_acc_rankings_actual = np.array([[1,2,3,4,5,6,7,8,9,10],
                                             [5,10,13,16,13,9,6,1,9,180],
                                             [7,10,1,12,17,21,24,27,31,37],
                                             [50,1,2,3,4,5,6,7,8,9]])
        norm_runtimes_actual = np.array([[1,2,3,4,5,6,7,8,9,10],
                                         [5,10,13,16,13,9,6,1,9,180],
                                         [7,10,1,12,17,21,24,27,31,37],
                                         [50,1,2,3,4,5,6,7,8,9]])
        summary_cells_acc_actual = np.array([[1,1,1,3,4,5,6,1,8,9],
                                             [50,10,13,16,17,21,24,27,31,180],
                                             [15.75,5.75,4.75,8.75,9.75,10.25,10.75,10.75,14.25,59],
                                             [6,6,2.5,8,9,7.5,6.5,7.5,9,23.5]])
        summary_cells_runtime_actual = np.array([[1,1,1,3,4,5,6,1,8,9],
                                                 [50,10,13,16,17,21,24,27,31,180],
                                                 [15.75,5.75,4.75,8.75,9.75,10.25,10.75,10.75,14.25,59],
                                                 [6,6,2.5,8,9,7.5,6.5,7.5,9,23.5]])

        accuracy_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                                 [20,40,52,64,52,36,24,4,36,720],
                                 [21,30,3,36,51,63,72,81,93,111],
                                 [100,2,4,6,8,10,12,14,16,18]])
        time_tbl = np.array([[1,2,3,4,5,6,7,8,9,10],
                             [20,40,52,64,52,36,24,4,36,720],
                             [21,30,3,36,51,63,72,81,93,111],
                             [100,2,4,6,8,10,12,14,16,18]])

        (norm_acc_rankings, norm_runtimes,
         summary_cells_acc, summary_cells_runtime) = calc_norm_summary_tables(accuracy_tbl, time_tbl)

        np.testing.assert_array_equal(norm_acc_rankings_actual, norm_acc_rankings)
        np.testing.assert_array_equal(norm_runtimes_actual, norm_runtimes)
        np.testing.assert_array_equal(summary_cells_acc_actual, summary_cells_acc)
        np.testing.assert_array_equal(summary_cells_runtime_actual, summary_cells_runtime)


    def TablesSetup(self):

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


    def test_calc_accuracy_runtime_tbls(self):

        accuracy_tbl_actual = np.array([[2, 4, 6],
                                        [4, 6, 8],
                                        [8, 16, 24]])
        time_tbl_actual = np.array([[2, 4, 6],
                                    [4, 6, 8],
                                    [8, 16, 24]])

        results_per_test = self.TablesSetup()[0]
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        accuracy_tbl, time_tbl = calc_accuracy_runtime_tbls(results_per_test, minimizers)

        np.testing.assert_array_equal(accuracy_tbl_actual, accuracy_tbl)
        np.testing.assert_array_equal(time_tbl_actual, time_tbl)


    def test_calc_summary_table(self):

        groups_norm_acc_actual = np.array([[1,2,3],[1,1.4,1.8],[1,1.25,1.5]])
        groups_norm_runtime_actual = np.array([[1,2,3],[1,1.4,1.8],[1,1.25,1.5]])

        group_results = self.TablesSetup()
        minimizers = ['Levenberg-Marquardt', 'Levenberg-MarquardtMD', 'Simplex']

        groups_norm_acc, groups_norm_runtime = calc_summary_table(minimizers, group_results)

        np.testing.assert_array_equal(groups_norm_acc_actual, groups_norm_acc)
        np.testing.assert_array_equal(groups_norm_runtime_actual, groups_norm_runtime)


    def PrepareTableHeader(self):

        tbl_header_top = ("+----------------------------------------------------------------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+"
                          "----------------------+")

        tbl_header_text = ("|                                                                            |"
                           "Minimizer1            |"
                           "Minimizer2            |"
                           "Minimizer3            |"
                           "Minimizer4            |"
                           "Minimizer5            |"
                           "Minimizer6            |"
                           "Minimizer7            |"
                           "Minimizer8            |"
                           "Minimizer9            |"
                           "Trust Region          |")

        tbl_header_bottom = ("+============================================================================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+"
                             "======================+")

        return tbl_header_top, tbl_header_text, tbl_header_bottom


    def GenerateRstTable(self):

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


    def test_build_rst_table(self):

        tbl_actual = self.GenerateRstTable()
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
        tbl = build_rst_table(minimizers, linked_problems, norm_acc_rankings,
                              comparison_type='accuracy', comparison_dim='',
                              using_errors=use_errors, color_scale=color_scale)

        self.assertEqual(tbl_actual, tbl)


    def test_display_name_for_minimizers(self):

        display_names_actual = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                                'Minimizer6','Minimizer7','Minimizer8','Minimizer9','Trust Region']

        names = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                 'Minimizer6','Minimizer7','Minimizer8','Minimizer9','DTRS']
        display_names = display_name_for_minimizers(names)

        self.assertListEqual(display_names_actual, display_names)


    def test_build_items_links(self):

        items_link_actual = ['Minimizers_weighted_comparison_in_terms_of_accuracy_nist_lower',
                             'Minimizers_weighted_comparison_in_terms_of_accuracy_nist_average',
                             'Minimizers_weighted_comparison_in_terms_of_accuracy_nist_higher',
                             'Minimizers_weighted_comparison_in_terms_of_accuracy_cutest',
                             'Minimizers_weighted_comparison_in_terms_of_accuracy_neutron_data']

        comparison_type = 'summary'
        comparison_dim = 'accuracy'
        using_errors = True

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)

        self.assertListEqual(items_link_actual, items_link)


        items_link_actual = 'FittingMinimizersComparisonDetailedWithWeights'

        comparison_type = 'accuracy'
        comparison_dim = ''
        using_errors = True

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)

        self.assertEqual(items_link_actual, items_link)


        items_link_actual = 'FittingMinimizersComparisonDetailed'

        comparison_type = 'runtime'
        comparison_dim = ''
        using_errors = False

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)

        self.assertEqual(items_link_actual, items_link)


        items_link_actual = ''

        comparison_type = 'pasta'
        comparison_dim = ''
        using_errors = False

        items_link = build_items_links(comparison_type, comparison_dim, using_errors)

        self.assertEqual(items_link_actual, items_link)


    def test_weighted_suffix_string(self):

        value = weighted_suffix_string(True)
        self.assertEqual(value, 'weighted')

        value = weighted_suffix_string(False)
        self.assertEqual(value, 'unweighted')


    def test_cell_len_rst_table(self):

        cell_len_actual = 22

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

        cell_len = calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)

        self.assertEqual(cell_len_actual, cell_len)


        cell_len_actual = 24

        columns_txt = ['Alabalaportocala12345678']
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

        cell_len = calc_cell_len_rst_table(columns_txt, items_link, cells, color_scale)

        self.assertEqual(cell_len_actual, cell_len)


    def test_format_cell_value_rst(self):

        value_text = format_cell_value_rst(value=180,
                                           color_scale=0,
                                           items_link=0)
        self.assertEqual(' 180', value_text)


        value_text_actual = ' :ref:`180 <FittingMinimizersComparisonDetailedWithWeights>`'
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'
        value_text = format_cell_value_rst(value=180,
                                           color_scale=0,
                                           items_link=items_link)
        self.assertEqual(value_text_actual, value_text)


        value_text_actual = " :ranking-low-4:`2`"
        value = 2
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=value,
                                           color_scale=color_scale,
                                           items_link=items_link)
        self.assertEqual(value_text_actual, value_text)


        value_text_actual = " :ranking-low-5:`180`    "
        value = 180
        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value_rst(value=value,
                                           width=25,
                                           color_scale=color_scale,
                                           items_link=items_link)
        self.assertEqual(value_text_actual, value_text)


    def test_calc_first_col_len(self):

        first_col_len_actual = 76

        cell_len = 22
        rows_txt = ["`Misra1a 1 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                    "`Misra1a 2 <http://www.itl.nist.gov/div898/strd/nls/data/misra1a.shtml>`__",
                    "`Lanczos3 1 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__",
                    "`Lanczos3 2 <http://www.itl.nist.gov/div898/strd/nls/data/lanczos3.shtml>`__"]
        first_col_len = calc_first_col_len(cell_len, rows_txt)

        self.assertEqual(first_col_len_actual, first_col_len)


    def test_build_rst_table_header_chunks(self):

        (tbl_header_top_actual, tbl_header_text_actual,
         tbl_header_bottom_actual) = self.PrepareTableHeader()

        first_col_len = 76
        cell_len = 22
        columns_txt = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4','Minimizer5',
                       'Minimizer6','Minimizer7','Minimizer8','Minimizer9','Trust Region']

        (tbl_header_top, tbl_header_text,
         tbl_header_bottom) = build_rst_table_header_chunks(first_col_len,
                                                            cell_len,
                                                            columns_txt)

        self.assertEqual(tbl_header_top_actual, tbl_header_top)
        self.assertEqual(tbl_header_text_actual, tbl_header_text)
        self.assertEqual(tbl_header_bottom_actual, tbl_header_bottom)


    def test_save_table_to_file(self):

        file_name_actual1 = "comparison_weighted_v3.8_acc_nist.txt"
        file_name_actual2 = "comparison_weighted_v3.8_acc_nist.html"
        file_name_actual3 = "comparison_weighted_v3.8_runtime_nist.txt"
        file_name_actual4 = "comparison_weighted_v3.8_runtime_nist.html"

        tbl_acc_indiv = self.GenerateRstTable()
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='acc', file_extension='txt')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='acc', file_extension='html')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='runtime', file_extension='txt')
        save_table_to_file(table_data=tbl_acc_indiv, errors=True, group_name='nist',
                           metric_type='runtime', file_extension='html')

        self.assertTrue(os.path.isfile(file_name_actual1))
        self.assertTrue(os.path.isfile(file_name_actual2))
        self.assertTrue(os.path.isfile(file_name_actual3))
        self.assertTrue(os.path.isfile(file_name_actual4))


if __name__ == "__main__":
    unittest.main()
