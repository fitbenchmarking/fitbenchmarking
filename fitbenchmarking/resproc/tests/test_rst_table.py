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

from resproc.rst_table import create
from resproc.rst_table import create_table_body
from resproc.rst_table import calc_cell_len
from resproc.rst_table import format_cell_value
from resproc.rst_table import calc_first_col_len
from resproc.rst_table import build_header_chunks
from resproc.rst_table import set_file_name

class RstTableTests(unittest.TestCase):

    def getRSTcurrentDir(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        current_dir = current_dir.replace("\\", "/")

        return current_dir

    def PrepareTableHeader(self):
        ''' Helper function that returns the headers used in making the rst table '''

        current_dir = self.getRSTcurrentDir()
        linked_problem = "`Misra1a 1 <file:///" + current_dir + \
                         "/dump/nist/VDPages/nist_lower_misra1a.html>`__"
        length_table = len(linked_problem)
        tbl_header_top = ("+" + "-"*length_table + "+" + ("-"*21 + "+")*10)
        tbl_header_text = ("|" + " "*length_table + "|" + "Minimizer1" + " "*11 + "|" + \
                           "Minimizer2" + 11*" " + "|" + "Minimizer3" + " "*11 +
                           "|" + \
                           "Minimizer4" + 11*" " + "|" + "Minimizer5" + " "*11 +
                           "|" + \
                           "Minimizer6" + 11*" " + "|" + "Minimizer7" + " "*11 +
                           "|" + \
                           "Minimizer8" + 11*" " + "|" + "Minimizer9" + " "*11 +
                           "|" + \
                           "Trust Region" + " "*9 + "|")
        tbl_header_bottom = ("+" + "="*length_table + "+" + ("="*21 + "+")*10)

        return tbl_header_top, tbl_header_text, tbl_header_bottom

    def GenerateTableBody(self):

        tbl_htop, tbl_htext, tbl_hbottom = self.PrepareTableHeader()
        tbl_footer = tbl_htop + '\n'
        tbl_body = '|`Misra1a 1 <file:///C:/Users/511/fitbenchmarking/' + \
                   'fitbenchmarking/resproc/tests/dump/nist/VDPages/' + \
                   'nist_lower_misra1a.html>`__| :ranking-top-1:`1`  | ' + \
                   ':ranking-low-4:`2`  | :ranking-low-4:`3`  |\n' + \
                   tbl_footer + '|`Misra1a 2 <file:///C:/Users/511/' + \
                   'fitbenchmarking/fitbenchmarking/resproc/tests/dump/' + \
                   'nist/VDPages/nist_lower_misra1a.html>`__| ' + \
                   ':ranking-low-5:`5`  | :ranking-low-5:`10` |' + \
                   ' :ranking-low-5:`13` |\n'

        return tbl_body

    def GenerateExpectedTable(self):

        tbl_htop, tbl_htext, tbl_hbottom = self.PrepareTableHeader()
        tbl_header = tbl_htop + '\n' + tbl_htext + '\n' + tbl_hbottom + '\n'
        tbl_footer = tbl_htop + '\n'
        tbl_body = self.GenerateTableBody()

        return tbl_header + tbl_body + tbl_footer

    def CalcCellLenParameters(self):

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

    def CreateTableInputData(self):

        current_dir = self.getRSTcurrentDir()
        columns_txt = ['Minimizer1','Minimizer2','Minimizer3','Minimizer4',
                       'Minimizer5', 'Minimizer6','Minimizer7','Minimizer8',
                       'Minimizer9', 'Trust Region']
        rows_txt = ["`Misra1a 1 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__",
                    "`Misra1a 2 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__"]
        cells = np.array([[1,2,3],
                          [5,10,13]])

        color_scale = [(1.1, 'ranking-top-1'),
                       (1.33, 'ranking-top-2'),
                       (1.75, 'ranking-med-3'),
                       (3, 'ranking-low-4'),
                       (float('nan'), 'ranking-low-5')]

        return columns_txt, rows_txt, cells, color_scale


    def test_create_produces_right_table(self):

        columns_txt, rows_txt, cells, color_scale = self.CreateTableInputData()

        table = create(columns_txt, rows_txt, cells, 'accuracy', '',
                       True, color_scale)
        table_expected = self.GenerateExpectedTable()

        self.assertEqual(table_expected, table)

    def test_createTableBody_produces_right_body(self):

        columns_txt, rows_txt, cells, color_scale = self.CreateTableInputData()
        items_link = 'FittingMinimizersComparisonDetailedWithWeights'
        first_col_len = len(rows_txt[0])
        tbl_header_top, tbl_header_text, tbl_header_bottom = \
        self.PrepareTableHeader()
        tbl_footer = tbl_header_top + '\n'

        tbl_body = create_table_body(cells, items_link, rows_txt, first_col_len,
                                     21, color_scale, tbl_footer)
        tbl_body_expected = self.GenerateTableBody() + tbl_footer

        self.assertEqual(tbl_body_expected, tbl_body)

    def test_calcCellLen_cell_len_smaller_than_maxheader_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = \
        self.CalcCellLenParameters()

        cell_len = calc_cell_len(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 21

        self.assertEqual(cell_len_expected, cell_len)


    def test_calcCellLen_cell_len_larger_than_max_header_return_cell_len(self):

        columns_txt, items_link, cells, color_scale = \
        self.CalcCellLenParameters()
        columns_txt = ['Alabalaportocala11345678']

        cell_len = calc_cell_len(columns_txt, items_link, cells, color_scale)
        cell_len_expected = 24

        self.assertEqual(cell_len_expected, cell_len)


    def test_FormatCellValue_no_colorscale_and_itemslink_return_valuetxt(self):

        value_text = format_cell_value(value=180, color_scale=0,
                                           items_link=0)
        self.assertEqual(' 180', value_text)


    def test_FormatCellValue_no_color_scale_return_value_text(self):

        items_link = 'FittingMinimizersComparisonDetailedWithWeights'

        value_text = format_cell_value(value=180, color_scale=0,
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

        value_text = format_cell_value(value=value, color_scale=color_scale,
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

        value_text = format_cell_value(value=value, width=25,
                                       color_scale=color_scale,
                                       items_link=items_link)
        value_text_expected = " :ranking-low-5:`180`    "

        self.assertEqual(value_text_expected, value_text)


    def test_calcFirstColLen_for_NIST_problem_Misra1a_and_Lanczos3(self):

        current_dir = self.getRSTcurrentDir()
        cell_len = 21
        rows_txt = ["`Misra1a 1 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__",
                    "`Misra1a 2 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__"]

        first_col_len = calc_first_col_len(cell_len, rows_txt)
        first_col_len_expected = len(rows_txt[0])

        self.assertEqual(first_col_len_expected, first_col_len)


    def test_buildHeaderChunks_return_header_chucks_Misra1a_prob_results(self):

        current_dir = self.getRSTcurrentDir()
        rows_txt = ["`Misra1a 1 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__",
                    "`Misra1a 2 <file:///" + current_dir + \
                    "/dump/nist/VDPages/nist_lower_misra1a.html>`__"]
        first_col_len = len(rows_txt[0])
        cell_len = 21
        columns_txt = ['Minimizer1', 'Minimizer2', 'Minimizer3', 'Minimizer4',
                       'Minimizer5', 'Minimizer6', 'Minimizer7', 'Minimizer8',
                       'Minimizer9', 'Trust Region']

        (tbl_header_top, tbl_header_text, tbl_header_bottom) = \
        build_header_chunks(first_col_len, cell_len, columns_txt)
        (tbl_header_top_expected, tbl_header_text_expected,
         tbl_header_bottom_expected) = self.PrepareTableHeader()

        self.assertEqual(tbl_header_top_expected, tbl_header_top)
        self.assertEqual(tbl_header_text_expected, tbl_header_text)
        self.assertEqual(tbl_header_bottom_expected, tbl_header_bottom)

    def test_setFileName_produces_correct_file_name(self):

        use_errors = True
        metric_type = 'acc'
        group_name = 'nist'
        results_dir = 'test_dir'

        file_name = set_file_name(use_errors, metric_type, group_name,
                                  results_dir)
        file_name_expected = 'test_dir' + os.sep + 'nist_acc_weighted_table.'

        self.assertEqual(file_name_expected, file_name)


if __name__ == "__main__":
    unittest.main()

