"""
Set up and build the visual display pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

from jinja2 import Environment, FileSystemLoader
import numpy as np
import os


def create_visual_pages(results_per_test, group_name, support_pages_dir,
                        options):
    """
    Creates the visual display html pages.

    :param results_per_test : results object
    :type results_per_test : list[list[list]]
    :param group_name : name of the problem group
    :type group_name : str
    :param results_dir : directory in which the results are saved
    :type results_dir : str
    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options

    :return : paths to created pages
    :rtype : list[str]
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
        name = create(prob_results,
                      group_name,
                      support_pages_dir,
                      count,
                      options)
        linked_problems.append(name)

    return linked_problems


def create(prob_results, group_name, support_pages_dir, count, options):
    """
    Creates a visual display page containing figures and other
    details about the best fit for a problem.

    :param prob_results : problem results objects containing results for
                          each minimizer and a certain fitting function
    :type prob_results : list
    :param group_name : name of the problem group
    :type group_name : str
    :param results_dir : directory in which the results are saved
    :type results_dir : str
    :param count : number of times a problem with the same name was
                   passed through this function, consecutively
    :type count : int
    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options

    :return : link to the visual display page (file path)
    :rtype : str
    """

    # Get the best result for a group
    best_result = min((result for result in prob_results),
                      key=lambda result: result.chi_sq
                      if result.chi_sq is not np.nan else np.inf)

    prob_name = best_result.problem.name
    prob_name = prob_name.replace(',', '')
    prob_name = prob_name.replace(' ', '_')

    file_name = (group_name + '_' + prob_name + '_' + str(count)).lower()
    file_path = os.path.join(support_pages_dir, file_name)

    fig_fit, fig_start = get_figure_paths(support_pages_dir,
                                          best_result,
                                          count)

    root = os.path.dirname(os.path.abspath(__file__))
    main_dir = os.path.dirname(root)
    html_page_dir = os.path.join(main_dir, "HTML_templates")
    env = Environment(loader=FileSystemLoader(html_page_dir))
    style_css = os.path.join(main_dir, 'HTML_templates/style_sheet.css')
    html_link = "{0}.html".format(file_path)

    template = env.get_template("results_template.html")

    with open(html_link, 'w') as fh:
        fh.write(template.render(
            css_style_sheet=style_css,
            title=prob_name,
            equation=best_result.problem.equation,
            make_plots=options.make_plots,
            initial_guess=best_result.ini_function_params,
            best_minimiser=best_result.minimizer,
            initial_plot=fig_start,
            min_params=best_result.fin_function_params,
            fitted_plot=fig_fit))

    return html_link


def get_figure_paths(support_pages_dir, result, count):
    """
    Get the paths to the figures used in the visual display page.

    :param support_pages_dir : directory containing the visual display pages
    :type support_pages_dir : str
    :param problem_name : name of the problem
    :type problem_name : str
    :param count : number of times a problem with the same name was
                   passed through this function, consecutively
    :type count : int

    :return : the paths to the required figures
    :rtype : tuple(str, str)
    """
    problem_name = result.problem.name
    figures_dir = os.path.join(support_pages_dir, "figures")
    figure_fits = os.path.join(
        figures_dir, "fit_for_{}_{}.png".format(problem_name, count))
    figure_strt = os.path.join(
        figures_dir, "start_for_{}_{}.png".format(problem_name, count))

    # If OS is Windows, then need to add prefix 'file:///'
    if os.name == 'nt':
        figure_fits = 'file:///' + figure_fits
        figure_strt = 'file:///' + figure_strt

    return figure_fits, figure_strt
