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


def build_page(prob_results, group_name, results_dir, count):
    """
    Builds a page containing details of the best fit for a problem.
    @param prob_results:: the list of results for a problem
    @param group_name :: the name of the group, e.g. "nist_lower"
    """

    # Get the best result for a group
    best_result = min((result for result in prob_results),
                       key=lambda result: result.chi_sq)
    problem_name = process_problem_name(best_result.problem.name)
    support_pages_dir, file_path, fit_details_tb, see_also_link = \
    setup_VDpage_misc(group_name, problem_name, best_result, results_dir, count)
    rst_link = generate_rst_link(file_path)

    figure_data, figure_fit, figure_start = \
    get_figure_paths(support_pages_dir, problem_name, count)
    rst_text = \
    create_rst_page(best_result.problem.name, figure_data, figure_start,
                    figure_fit, fit_details_tbl, best_result.minimizer,
                    see_also_link)

    save_VDpages(rst_text, problem_name, file_path)

    return rst_link


def create_rst_page(name, figure_data, figure_start, figure_fit, details_table,
                    minimizer, see_also_link):
    """
    Creates an rst page containing a title and 3 figures, with a detailed
    table about the fit on the last figure.
    """

    space = "|\n|\n|\n\n"
    title = generate_rst_title(name)
    data_plot = generate_rst_data_plot(figure_data)
    starting_plot = generate_rst_starting_plot(figure_start)
    solution_plot = generate_rst_solution_plot(figure_fit, details_table,
                                               minimizer)

    rst_text = title + space + data_plot + starting_plot + solution_plot + \
               space + see_also_link

    return rst_text


def process_problem_name(problem_name):
    """
    Remove commas and replace space with underscore in problem name
    """

    problem_name = problem_name.replace(',', '')
    problem_name = problem_name.replace(' ','_')

    return problem_name


def generate_rst_link(file_path):
    """
    """

    rst_file_path = file_path.replace('\\', '/')
    if os.name == 'nt':
        rst_link = "<file:///" + rst_file_path + "." + FILENAME_EXT_HTML + \
                   ">`__"
    else:
        rst_link = "<" + rst_file_path + "." + FILENAME_EXT_HTML + ">`__"

    return rst_link


def setup_nist_VDpage_misc(linked_name, function_def, results_dir):
    """
    """

    support_pages_dir = os.path.join(results_dir, "nist", "tables",
                                     "support_pages")
    details_table = fit_details_rst_table(function_def)
    see_also_link = 'See also:\n ' + linked_name + \
                    '\n on NIST website\n\n'

    return support_pages_dir, details_table, see_also_link


def setup_neutron_VDpage_misc(function_def, results_dir):
    """
    Helper function that sets up the directory, function details table
    and see also link for the NEUTRON data
    """
    support_pages_dir = os.path.join(results_dir, "neutron", "tables",
                                     "support_pages")
    details_table = fit_details_rst_table(function_def)
    see_also_link = ''

    return support_pages_dir, details_table, see_also_link


def setup_VDpage_misc(group_name, problem_name, res_obj, results_dir, count):
    """
    Setup miscellaneous data for visual display page.
    """
    # Group specific path and other misc stuff
    if 'nist' in group_name:
        support_pages_dir, fit_details_tbl, see_also_link = \
        setup_nist_VDpage_misc(res_obj.problem.linked_name,
                               res_obj.function_def, results_dir)
    elif 'neutron' in group_name:
        support_pages_dir, fit_details_tbl, see_also_link = \
        setup_neutron_VDpage_misc(res_obj.function_def, results_dir)

    file_name = (group_name + '_' + problem_name + '_' + str(count)).lower()
    file_path = os.path.join(support_pages_dir, file_name)

    return support_pages_dir, file_path, fit_details_tbl, see_also_link


def get_figure_paths(support_pages_dir, problem_name, count):

    figures_dir = os.path.join(support_pages_dir, "figures")
    figure_data = os.path.join(figures_dir, "Data_Plot_" + problem_name +
                               "_" + str(count) + ".png")
    figure_fits = os.path.join(figures_dir, "Fit_for_" + problem_name +
                               "_" + str(count) + ".png")
    figure_strt = os.path.join(figures_dir, "start_for_" + problem_name +
                               "_" + str(count) + ".png")

    # If OS is Windows, then need to add prefix 'file:///'
    if os.name == 'nt':
        figure_data = 'file:///' + figure_data
        figure_fits = 'file:///' + figure_fits
        figure_strt = 'file:///' + figure_strt

    return figure_data, figure_fits, figure_strt


def generate_rst_title(problem_name):
    """
    Helper function that generates a title for an rst page, containing
    the name of the problem.
    """

    title = '=' * len(problem_name) + '\n'
    title += problem_name + '\n'
    title += '=' * len(problem_name) + '\n\n'

    return title


def generate_rst_data_plot(figure_data):
    """
    Helper function that generates an rst figure of the data plot png image
    contained at path figure_data.
    """

    data_plot = 'Data Plot' + '\n'
    data_plot += ('-' * len(data_plot)) + '\n\n'
    data_plot += '*Plot of the data considered in the problem*\n\n'
    data_plot += ('.. image:: ' + figure_data + '\n' +
                  '   :align: center' + '\n\n')

    return data_plot


def generate_rst_starting_plot(figure_start):
    """
    Helper function that generates an rst figure of the starting guess plot
    png image contained at path figure_start.
    """
    starting_plot = 'Plot of the initial starting guess' + '\n'
    starting_plot += ('-' * len(starting_plot)) + '\n\n'
    starting_plot += '*Minimizer*: Levenberg-Marquardt \n\n'
    starting_plot += ('.. figure:: ' + figure_start  + '\n' +
                      '   :align: center' + '\n\n')

    return starting_plot


def generate_rst_solution_plot(figure_fit, fit_function_details_table,
                               minimizer):
    """
    Helper function that generates an rst figure of the fitted problem
    png image contained at path figure_fit.
    """

    solution_plot = 'Plot of the solution found' + '\n'
    solution_plot += ('-' * len(solution_plot)) + '\n\n'
    solution_plot += '*Minimizer*: ' + minimizer + '\n\n'
    solution_plot += '*Functions*:\n\n'
    solution_plot += fit_function_details_table
    solution_plot += ('.. figure:: ' + figure_fit + '\n' +
                      '   :align: center' + '\n\n')

    return solution_plot


def save_VDpages(rst_text, prob_name, file_path):
    """
    Helper function that saves the rst page into text and html after
    converting it to html.
    """

    html = publish_string(rst_text, writer_name='html')
    with open(file_path + '.' + FILENAME_EXT_TXT, 'w') as visual_rst:
        print(rst_text, file=visual_rst)
        logger.info('Saved {prob_name}.{extension} to {working_directory}'.
                     format(prob_name=prob_name, extension=FILENAME_EXT_TXT,
                            working_directory=file_path))

    with open(file_path + '.' + FILENAME_EXT_HTML, 'w') as visual_html:
        print(html, file=visual_html)
        logger.info('Saved {prob_name}.{extension} to {working_directory}'.
                     format(prob_name=prob_name, extension=FILENAME_EXT_HTML,
                            working_directory=file_path))
