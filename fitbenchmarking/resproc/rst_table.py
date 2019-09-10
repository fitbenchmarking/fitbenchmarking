"""
Set up and build the visual display pages for various types of problems.
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

import os
import numpy as np
from docutils.core import publish_string
from resproc.misc import build_items_links
from resproc.misc import display_name_for_minimizers
from resproc.misc import weighted_suffix_string
from utils.logging_setup import logger


# Directory of this script (e.g. in source)
SCRIPT_DIR = os.path.dirname(__file__)


def create(columns_txt, rows_txt, cells, comparison_type, comparison_dim,
           using_errors, color_scale=None, comparison_mode='abs'):
    """
    Creates a rst table of accuracy and runtime tables obtained
    through fitting a certain problem set by using various
    minimizers and a fitting software.

    @param columns_txt :: array of minimizers used in fitting
    @param rows_txt :: array of the problems that were fitted
    @param cells :: numpy array of the results (either runtime or accuracy)
    @param comparison_type :: the comparison type
    @param comparison_dim :: the comparison dimension, either acc or runtime
    @param using_errors :: boolean whether to use errors or not
    @param color_scale :: color scale for coloring the cells
    @param comparison_mode :: str to select between 'abs', 'rel', 'both' for
                              the style of comparison returned

    @returns :: rst table of the results
    """

    columns_txt = display_name_for_minimizers(columns_txt)
    items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)

    cell_len = calc_cell_len(columns_txt, items_link, cells, color_scale, mode=comparison_mode)

    # The first column tends to be disproportionately long if it has a link
    first_col_len = calc_first_col_len(cell_len, rows_txt)
    tbl_htop, tbl_htext, tbl_hbottom = \
        build_header_chunks(first_col_len, cell_len, columns_txt)

    tbl_header = tbl_htop + '\n' + tbl_htext + '\n' + tbl_hbottom + '\n'
    tbl_footer = tbl_htop + '\n'
    tbl_body = create_table_body(cells, items_link, rows_txt, first_col_len,
                                 cell_len, color_scale, tbl_footer, mode=comparison_mode)

    return tbl_header + tbl_body


def create_table_body(cells, items_link, rows_txt, first_col_len, cell_len,
                      color_scale, tbl_footer, mode):
    """
    Creates the body of the rst table that holds all the fitting results.

    @param cells :: numpy array of the results (either runtime or accuracy)
    @param items_link :: link to the items
    @param rows_txt :: array of the problems that were fitted
    @param first_col_len :: the length of the first column (contains
                            the function names)
    @param cell_len :: the length of the cells in the table
    @param color_scale :: color scale for coloring the cells
    @param tbl_footer :: the rst footer of the table
    @param mode :: str to select between 'abs', 'rel', 'both' for
                   the style of comparison returned

    @returns :: the rst table body
    """

    tbl_body = ''
    for row in range(0, cells.shape[0]):

        all_fit_failed_status = ''
        if np.isnan(cells[row, :, 0]).all():
            all_fit_failed_status = '(all fit failed)'

        tbl_body += '|' + rows_txt[row].ljust(first_col_len-len(all_fit_failed_status), ' ')\
                    + all_fit_failed_status + '|'

        for col in range(0, cells.shape[1]):
            tbl_body += format_cell_value(value=cells[row, col],
                                          width=cell_len,
                                          color_scale=color_scale,
                                          items_link=items_link,
                                          mode=mode)
            tbl_body += '|'

        tbl_body += '\n' + tbl_footer

    return tbl_body


def calc_cell_len(columns_txt, items_link, cells, color_scale=None, mode='abs'):
    """
    Calculates the cell length of the rst table.

    @param columns_txt :: array of minimizers used in fitting
    @param items_link :: link to the items
    @param cells :: numpy array of the results (either runtime or accuracy)
    @param color_scale :: color scale for coloring the cells
    @param mode :: str to select between 'abs', 'rel', 'both' for
                   the style of comparison returned

    @returns :: the cell length of the rest table
    """

    max_header = len(max((col for col in columns_txt), key=len))
    max_value = max(cells.reshape((-1, 2)), key=lambda x: len(cell_to_string(x, mode)))
    max_item = determine_max_item(items_link)
    cell_len = len(format_cell_value(value=max_value,
                                     color_scale=color_scale,
                                     items_link=max_item,
                                     mode=mode).strip()) + 2
    if cell_len < max_header:
        cell_len = max_header

    return cell_len


def determine_max_item(items_link):
    """
    Determines the item that has the maximum length.

    @param items_links :: items_link string or array

    @returns :: the maximum items link
    """

    max_item = None
    if isinstance(items_link, list):
        max_item = max(items_link, key=len)
    else:
        max_item = len(items_link)

    return max_item


def calc_first_col_len(cell_len, rows_txt):
    """
    Calculates the first column length as it tends to be disproportionately
    long.

    @param cell_len :: the length of the cells in the table
    @param rows_txt :: array of the problems that were fitted

    @returns :: the length of the first column
    """

    first_col_len = cell_len
    for row_name in rows_txt:
        name_len = len(row_name)
        if name_len > first_col_len:
            first_col_len = name_len

    first_col_len += 20

    return first_col_len


def build_header_chunks(first_col_len, cell_len, columns_txt):
    """
    Creates the header chunks for the rst table.

    @param first_col_len :: the length of the first column (contains
                            the function names)
    @param cell_len :: the length of the cells in the table
    @param columns_txt :: array of minimizers used in fitting

    @results :: the top, middle and bottom of the rst table header
    """

    tbl_header_top = '+'
    tbl_header_text = '|'
    tbl_header_bottom = '+'

    # First column in the header for the name of the test or statistics
    tbl_header_top += '-'.ljust(first_col_len, '-') + '+'
    tbl_header_text += ' '.ljust(first_col_len, ' ') + '|'
    tbl_header_bottom += '='.ljust(first_col_len, '=') + '+'
    for col_name in columns_txt:
        tbl_header_top += '-'.ljust(cell_len, '-') + '+'
        tbl_header_text += col_name.ljust(cell_len, ' ') + '|'
        tbl_header_bottom += '='.ljust(cell_len, '=') + '+'

    return tbl_header_top, tbl_header_text, tbl_header_bottom


def format_cell_value(value, width=None, color_scale=None, items_link=None, mode='abs'):
    """
    Formats the cell values and adds color if a color scale is provided.

    @param value :: the values of the color if it is added
    @param width :: the width of the cell if it is given
    @param color_scale :: color scale for coloring the cells
    @param items_links :: items_link string or array
    @param mode :: str to select between 'abs', 'rel', 'both' for
                   the style of comparison returned

    @returns :: the correct value text string
    """

    value_text = cell_to_string(value, mode)

    if not color_scale:
        value_text = no_color_scale_cv(items_link, value_text)
    else:
        value_text = color_scale_cv(color_scale, value[1], value_text)

    if width is not None:
        value_text = value_text.ljust(width, ' ')

    return value_text


def no_color_scale_cv(items_link, value_text):
    """
    Creates the values text if no color scale is provided.

    @param items_links :: items_link string or array
    @param value_text :: text representing the value for the cell

    @returns :: the no coloring value text string, containing
                the items_links
    """

    if not items_link:
        value_text = ' {}'.format(value_text)
    else:
        value_text = ' :ref:`{0} <{1}>`'.format(value_text, items_link)

    return value_text


def color_scale_cv(color_scale, value, text):
    """
    Creates the values text if a color scale is provided.

    @param color_scale :: color scale for coloring the cells
    @param value :: the values of the color if it is added
    @param text :: the cell text

    @returns :: the value text with added color values
    """

    color = ''
    for color_descr in color_scale:
        if value <= color_descr[0]:
            color = color_descr[1]
            break
    if not color:
        color = color_scale[-1][1]

    value_text = " :{0}:`{1}`".format(color, text)

    return value_text


def save_table_to_file(results_dir, table_data, use_errors, group_name,
                       metric_type, file_extension):
    """
    Saves the rst table to a file, both in text and html formats.

    @param results_dir :: directory where results are located
    @param table_data :: the data of the table
    @param use_errors :: boolean with whether or not to use errors
    @param group_name :: the name of the problem group for
                         which the table is built
    @param metric_type :: either accuracy or runitme data
    @param file_extension :: text or html

    @returns :: html and/or text tables of the results
    """

    file_name = set_file_name(use_errors, metric_type, group_name, results_dir)

    if file_extension == 'html':
        table_data = convert_rst_to_html(table_data)

    with open(file_name + file_extension, 'w') as tbl_file:
        print(table_data, file=tbl_file)

    logger.info('Saved {file_name}{extension} to {working_directory}'.
                format(file_name=os.path.basename(file_name), extension=file_extension,
                       working_directory=results_dir[results_dir.find('fitbenchmarking'):]))


def set_file_name(use_errors, metric_type, group_name, results_dir):
    """
    Sets the name of the html/text table file that is saved.

    @param use_errors :: boolean with whether or not to use errors
    @param metric_type :: either accuracy or runtime data
    @param group_name :: the name of the problem group for
                         which the table is built
    @param results_dir :: directory where results are located
    """

    file_name = ('{group_name}_{metric_type}_{weighted}_table.'
                 .format(weighted=weighted_suffix_string(use_errors),
                         metric_type=metric_type, group_name=group_name))
    file_name = os.path.join(results_dir, file_name)

    return file_name


def convert_rst_to_html(table_data):
    """
    Converts the rst tables into html.

    @param table_data :: rst table containing all the data

    @returns :: the rst table in html
    """

    rst_content = '.. include:: ' + \
                  str(os.path.join(SCRIPT_DIR, 'color_definitions.txt'))
    rst_content += '\n' + table_data
    table_data = publish_string(rst_content, writer_name='html')

    return table_data


def cell_to_string(value, mode='abs'):
    """
    Utility function to choose display mode. Options for mode are:
     'abs' - The value as it was returned
     'rel' - The value relative to other values (smallest is 1)
     'both' - The 'abs' result followed by the 'rel' result in brackets

    @param value :: The value to convert
    @param mode :: The display mode

    @returns :: String with the correct formatting 
    """

    if mode not in ['abs', 'rel', 'both']:
        raise ValueError('Could not decifer mode "{}". Please select from "abs", "rel", or "both"'.format(mode))

    if mode == 'both':
        return '{:.4g} ({:.4g})'.format(value[0], value[1])  # NOQA
    elif mode == 'rel':
        return '{:.4g}'.format(value[1])  # NOQA
    else:
        return '{:.4g}'.format(value[0])  # NOQA