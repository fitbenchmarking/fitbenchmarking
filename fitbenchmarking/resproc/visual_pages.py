"""
Set up and build the visual display pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

import numpy as np
import os
from docutils.core import publish_string
from fitbenchmarking.utils.logging_setup import logger
from jinja2 import Environment, FileSystemLoader
import os

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
        name = create(prob_results, group_name, results_dir, count)
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

    prob_name = best_result.problem.name
    prob_name = prob_name.replace(',', '')
    prob_name = prob_name.replace(' ', '_')

    support_pages_dir, file_path, see_also_link = \
        setup_page_misc(group_name, prob_name,
                        best_result, results_dir, count)
    fig_data, fig_fit, fig_start = \
        get_figure_paths(support_pages_dir, prob_name, count)

    root = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(root))

    template = env.get_template('results_template.html')
    html_link = "{0}.html".format(file_path)

    with open(html_link, 'w') as fh:
        fh.write(template.render(
            title=prob_name,
            equation=best_result.problem.equation,
            initial_guess=best_result.ini_function_def.split("|")[1],
            best_minimiser=best_result.minimizer,
            initial_plot=fig_start,
            min_params=best_result.fin_function_def.split("|")[1],
            fitted_plot=fig_fit))

    return html_link


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
