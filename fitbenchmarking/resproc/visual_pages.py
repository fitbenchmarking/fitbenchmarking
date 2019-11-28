"""
Set up and build the visual display pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
import os
from docutils.core import publish_string
from fitbenchmarking.resproc import fitdetails_tbls
from fitbenchmarking.utils.logging_setup import logger

# Some naming conventions for the output files
FILENAME_EXT_TXT = 'txt'
FILENAME_EXT_HTML = 'html'


def create_linked_probs(results_per_test, group_name, results_dir):
    """
    Creates the problem names with links to the visual display pages
    in rst.

    @param results_per_test :: results object
    @param group_name :: name of the problem group
    @param results_dir :: directory in which the results are saved

    @returns :: array of the problem names with the links in rst
    """

    # Count keeps track if it is the same problem but different starting point
    prev_name = ''
    count = 1

    linked_problems = []
    for test_idx, prob_results in enumerate(results_per_test):
        name = results_per_test[test_idx][0].problem.name
        if name == prev_name:
            count += 1
        else:
            count = 1
        prev_name = name
        name_index = name + ' ' + str(count)
        name = '`' + name_index + ' ' + \
               create(prob_results, group_name, results_dir, count)
        linked_problems.append(name)

    return linked_problems


def create(prob_results, group_name, results_dir, count):
    """
    Creates a visual display page containing figures and other
    details about the best fit for a problem.

    @param prob_results :: problem results objects containing results for
                           each minimizer and a certain fitting function
    @param group_name :: name of the group the problem belongs to
    @param results_dir :: results directory
    @param count :: number of times a problem with the same name was
                    passed through this function, consecutively

    @returns :: link to the visual display page (file path)
    """

    # Get the best result for a group
    best_result = min((result for result in prob_results),
                      key=lambda result: result.chi_sq
                      if result.chi_sq is not np.nan else np.inf)

    problem_name = process_problem_name(best_result.problem.name)
    support_pages_dir, file_path, see_also_link = setup_page_misc(
        group_name, problem_name, best_result, results_dir, count)
    rst_link = generate_rst_link(file_path)

    ini_details_tbl, fin_details_tbl = \
        setup_detail_page_tbls(best_result.ini_function_def,
                               best_result.fin_function_def)

    fig_data, fig_fit, fig_start = \
        get_figure_paths(support_pages_dir, problem_name, count)
    rst_text = \
        create_rst_page(best_result.problem.name, fig_data, fig_start, fig_fit,
                        best_result.minimizer, see_also_link, ini_details_tbl,
                        fin_details_tbl)
    save_page(rst_text, problem_name, file_path)

    return rst_link


def create_rst_page(name, fig_data, fig_start, fig_fit, minimizer,
                    see_also_link, ini_det_tbl, fin_det_tbl):
    """
    Creates an rst page containing a title and 3 figures, with detailed
    tables about the fit on the last two figures.

    @param name :: string containing the name of the problem
    @param figure_data :: path to the raw plot of the data (.png image)
    @param figure_start :: path to the starting guess plot (.png image)
    @param figure_fit :: path to the best fit plot (.png image)
    @param details_table :: the plot details table in rst
    @param minimizer :: name of the minimizer that was used
    @param see_also_link :: links to an alternative page
                            if documentation on the problem exists.

    @returns :: the visual display page written in rst
    """

    space = "|\n|\n|\n\n"
    title = generate_rst_title(name)
    data_plot = generate_rst_data_plot(fig_data)
    starting_plot = generate_rst_starting_plot(fig_start, ini_det_tbl)
    solution_plot = generate_rst_solution_plot(fig_fit, minimizer, fin_det_tbl)

    rst_text = title + space + data_plot + starting_plot + solution_plot + \
        space + see_also_link

    return rst_text


def process_problem_name(problem_name):
    """
    Remove commas and replace space with underscore in problem name

    @param problem_name :: name of the problem that is being considered

    @returns :: the processed problem name
    """

    problem_name = problem_name.replace(',', '')
    problem_name = problem_name.replace(' ', '_')

    return problem_name


def generate_rst_link(file_path):
    """
    Generate the rst link, dependent on the OS, i.e. windows needs
    an extra file:/// at the start to link correctly.

    @param file_path :: the path to the visual display page

    @returns :: the proper rst_link
    """

    rst_file_path = file_path.replace('\\', '/')
    if os.name == 'nt':
        rst_link = "<file:///" + rst_file_path + "." + FILENAME_EXT_HTML + \
                   ">`__"
    else:
        rst_link = "<" + rst_file_path + "." + FILENAME_EXT_HTML + ">`__"

    return rst_link


def setup_detail_page_tbls(initial_fdef, final_fdef):

    initial_details_tbl = fitdetails_tbls.create(initial_fdef)
    if final_fdef is not None:
        final_details_tbl = fitdetails_tbls.create(final_fdef)
    else:
        final_details_tbl = "None - fit failed\n\n"

    return initial_details_tbl, final_details_tbl


def setup_page_misc(group_name, problem_name, res_obj, results_dir, count):
    """
    Sets up some miscellaneous things for the visual display pages.

    @param group_name :: name of the group containing the
                         current problem
    @param problem_name :: name of the problem
    @param res_obj :: problem result object
    @param results_dir :: directory containing the results
    @param count :: number of times a problem with the same name was
                    passed through this function, consecutively

    @returns :: the directory in which the visual display pages go
                the file path to the visual display page that is
                currently being made
                the fit details table and the see also link
    """

    # Group specific path and other misc stuff

    support_pages_dir = os.path.join(results_dir, group_name, "support_pages")
    if not os.path.exists(support_pages_dir):
        os.makedirs(support_pages_dir)
    see_also_link = ''
    if 'nist' in group_name.lower():
        link = ("`{0} <http://www.itl.nist.gov/div898/strd/nls/data"
                "/{1}.shtml>`__".format(problem_name, problem_name.lower()))
        see_also_link = 'See also:\n ' + link + '\n on NIST website\n\n'

    file_name = (group_name + '_' + problem_name + '_' + str(count)).lower()
    file_path = os.path.join(support_pages_dir, file_name)

    return support_pages_dir, file_path, see_also_link


def get_figure_paths(support_pages_dir, problem_name, count):
    """
    Get the paths to the figures used in the visual display page.

    @param support_pages_dir :: directory containing the visual
                                display pages
    @param problem_name :: name of the problem
    @param count :: number of times a problem with the same name was
                    passed through this function, consecutively

    @returns :: the paths to the required figures
    """

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

    @param problem_name :: name of the problem

    @returns :: the title in rst
    """

    title = '=' * len(problem_name) + '\n'
    title += problem_name + '\n'
    title += '=' * len(problem_name) + '\n\n'

    return title


def generate_rst_data_plot(figure_data):
    """
    Helper function that generates an rst figure of the data plot png image
    contained at path figure_data.

    @param figure_data :: path to the raw data plot

    @returns :: the data plot section in rst
    """

    data_plot = 'Data Plot' + '\n'
    data_plot += ('-' * len(data_plot)) + '\n\n'
    data_plot += '*Plot of the data considered in the problem*\n\n'
    data_plot += ('.. image:: ' + figure_data + '\n' +
                  '   :align: center' + '\n\n')

    return data_plot


def generate_rst_starting_plot(figure_start, initial_details_tbl):
    """
    Helper function that generates an rst figure of the starting guess plot
    png image contained at path figure_start.

    @param figure_start :: path to the starting guess figure
    @param initial_details_tbl :: table in rst containing the initial guess
                                  details

    @returns :: the starting guess plot section in rst
    """
    starting_plot = 'Plot of the initial starting guess' + '\n'
    starting_plot += ('-' * len(starting_plot)) + '\n\n'
    starting_plot += '*Functions*:\n\n'
    starting_plot += initial_details_tbl
    starting_plot += ('.. figure:: ' + figure_start + '\n' +
                      '   :align: center' + '\n\n')

    return starting_plot


def generate_rst_solution_plot(figure_fit, minimizer, final_details_tbl):
    """
    Helper function that generates an rst figure of the fitted problem
    png image contained at path figure_fit.

    @param figure_data :: path to the best fit figure
    @param minimizer :: name of minimizer used in obtaining the fit

    @returns :: the fit solution section in rst
    """

    solution_plot = 'Plot of the solution found' + '\n'
    solution_plot += ('-' * len(solution_plot)) + '\n\n'
    solution_plot += '*Minimizer*: ' + minimizer + '\n\n'
    solution_plot += '*Functions*:\n\n'
    solution_plot += final_details_tbl
    solution_plot += ('.. figure:: ' + figure_fit + '\n' +
                      '   :align: center' + '\n\n')

    return solution_plot


def save_page(rst_text, prob_name, file_path):
    """
    Helper function that saves the rst page into text and html after
    converting it to html.

    @param rst_text :: page to be converted/saved in rst
    @param prob_name :: name of the problem
    @param file_path :: path to where the file is going to be saved

    @returns :: html/txt visual display page saved at file_path
    """

    html = publish_string(rst_text, writer_name='html')
    with open(file_path + '.' + FILENAME_EXT_TXT, 'w') as visual_rst:
        print(rst_text, file=visual_rst)
        logger.info('Saved {prob_name}.{extension} to {working_directory}'.
                    format(prob_name=prob_name, extension=FILENAME_EXT_TXT,
                           working_directory=file_path[
                               file_path.find('fitbenchmarking'):]))

    with open(file_path + '.' + FILENAME_EXT_HTML, 'w') as visual_html:
        print(html, file=visual_html)
        logger.info('Saved {prob_name}.{extension} to {working_directory}'.
                    format(prob_name=prob_name, extension=FILENAME_EXT_HTML,
                           working_directory=file_path[
                               file_path.find('fitbenchmarking'):]))
