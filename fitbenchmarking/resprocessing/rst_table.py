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
from docutils.core import publish_string


# Directory of this script (e.g. in source)
SCRIPT_DIR = os.path.dirname(__file__)


def create(columns_txt, rows_txt, cells, comparison_type, comparison_dim,
           using_errors, color_scale=None):
    """
    """

    columns_txt = display_name_for_minimizers(columns_txt)
    items_link = \
    build_items_links(comparison_type, comparison_dim, using_errors)
    cell_len = calc_cell_len(columns_txt, items_link, cells, color_scale)

    # The first column tends to be disproportionately long if it has a link
    first_col_len = calc_first_col_len(cell_len, rows_txt)
    tbl_htop, tbl_htext, tbl_hbottom = \
    build_header_chunks(first_col_len, cell_len, columns_txt)

    tbl_header = tbl_htop + '\n' + tbl_htext + '\n' + tbl_hbottom + '\n'
    tbl_footer = tbl_htop + '\n'
    tbl_body = create_table_body(cells, items_link, rows_txt, first_col_len,
                                 cell_len, color_scale, tbl_footer)

    return tbl_header  + tbl_body


def create_table_body(cells, items_link, rows_txt, first_col_len, cell_len,
                      color_scale, tbl_footer):
    """
    Creates the body of the rst table that holds all the fitting results.
    """

    tbl_body = ''
    for row in range(0, cells.shape[0]):
        link = create_link(items_link)
        tbl_body += '|' + rows_txt[row].ljust(first_col_len, ' ') + '|'
        for col in range(0, cells.shape[1]):
            tbl_body += format_cell_value(cells[row, col], cell_len,
                                          color_scale, link)
            tbl_body += '|'

        tbl_body += '\n' + tbl_footer

    return tbl_body


def create_link(items_link):
    """
    Pick either individual or group link
    """

    link = None
    if isinstance(items_link, list):
        link = items_link[row]
    else:
        link = items_link

    return link


def calc_cell_len(columns_txt, items_link, cells, color_scale=None):
    """
    """

    max_header = len(max((col for col in columns_txt), key=len))
    max_value = max(("%.4g" % cell for cell in np.nditer(cells)), key=len)
    max_item = determine_max_item(items_link)
    cell_len = len(format_cell_value(value=float(max_value),
                                     color_scale=color_scale,
                                     items_link=max_item).strip()) + 2
    if cell_len < max_header:
        cell_len = max_header

    return cell_len


def determine_max_item(items_link):
    """
    """

    max_item = None
    if isinstance(items_link, list):
        max_item = max(items_link, key=len)
    else:
        max_item = len(items_link)

    return max_item


def calc_first_col_len(cell_len, rows_txt):
    """
    """

    first_col_len = cell_len
    for row_name in rows_txt:
        name_len = len(row_name)
        if name_len > first_col_len:
            first_col_len = name_len

    return first_col_len


def build_header_chunks(first_col_len, cell_len, columns_txt):
    """
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


def format_cell_value(value, width=None, color_scale=None, items_link=None):
    """
    """
    if not color_scale:
        value_text = no_color_scale_cv(items_link)
    else:
        value_text = color_scale_cv

    if width is not None:
        value_text = value_text.ljust(width, ' ')

    return value_text


def no_color_scale_cv(items_link):
    """
    """

    if not items_link:
        value_text = ' {0:.4g}'.format(value)
    else:
        value_text = ' :ref:`{0:.4g} <{1}>`'.format(value, items_link)

    return value_text


def color_scale_cv(color_scale):
    """
    """

    color = ''
    for color_descr in color_scale:
        if value <= color_descr[0]:
            color = color_descr[1]
            break
    if not color:
        color = color_scale[-1][1]

    value_text = " :{0}:`{1:.4g}`".format(color, value)

    return value_text


def save_table_to_file(results_dir, table_data, errors, group_name, metric_type,
                       file_extension):
    """
    """

    file_name = set_file_name(errors, metric_type, group_name, results_dir)

    if file_extension == 'html':
        table_data = convert_rst_to_html(table_data)

    with open(file_name + file_extension, 'w') as tbl_file:
        print(table_data, file=tbl_file)

    logger.info('Saved {file_name}{extension} to {working_directory}'.
                 format(file_name=file_name, extension=file_extension,
                        working_directory=results_dir))


def set_file_name(errors, metric_type, group_name, results_dir):
    """
    """

    file_name = ('{group_name}_{metric_type}_{weighted}_table.'
                 .format(weighted=weighted_suffix_string(errors),
                         metric_type=metric_type, group_name=group_name))
    file_name = os.path.join(results_dir, file_name)

    return file_name


def convert_rst_to_html(table_data):
    """
    """

    rst_content = '.. include:: ' + str(os.path.join(SCRIPT_DIR,
                                                     'color_definitions.txt'))
    rst_content += '\n' + table_data
    table_data = publish_string(rst_content, writer_name='html')

    return table_data
