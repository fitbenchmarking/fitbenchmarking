"""
Set up and build the visual display pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

from jinja2 import Environment, FileSystemLoader
import numpy as np
import os

from fitbenchmarking.results_processing import plots


def create_linked_probs(results_per_test, group_name, results_dir, options):
    """
    Creates the problem names with links to the visual display pages
    in rst.

    :param results_per_test : results object
    :type results_per_test : list[list[list]]
    :param group_name : name of the problem group
    :type group_name : str
    :param results_dir : directory in which the results are saved
    :type results_dir : str
    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options

    :return : array of the problem names with the links in rst
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
        name = create(prob_results, group_name, results_dir, count, options)
        linked_problems.append(name)

    return linked_problems


def create(prob_results, group_name, results_dir, count, options):
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
    directory = os.path.join(results_dir, group_name)

    plot = plots.Plot(problem=best_result.problem,
                      options=options,
                      count=count,
                      group_results_dir=directory)
    plot.plot_initial_guess()
    plot.plot_best_fit(best_result.minimizer, best_result.params)

    support_pages_dir, file_path = \
        get_filename_and_path(group_name, prob_name,
                              best_result, results_dir, count)
    fig_fit, fig_start = \
        get_figure_paths(support_pages_dir, prob_name, count)

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
            initial_guess=best_result.ini_function_params,
            best_minimiser=best_result.minimizer,
            initial_plot=fig_start,
            min_params=best_result.fin_function_params,
            fitted_plot=fig_fit))

    return html_link


def get_filename_and_path(group_name, problem_name, res_obj,
                          results_dir, count):
    """
    Sets up some miscellaneous things for the visual display pages.

    :param group_name : name of the group containing the current problem
    :type group_name : str
    :param problem_name : name of the problem
    :type problem_name : str
    :param res_obj : best results object
    :type res_obj : results object
    :param results_dir : directory in which the results are saved
    :type results_dir : str
    :param count : number of times a problem with the same name was
                   passed through this function, consecutively
    :type count : int

    :return : the directory in which the visual display pages go
              the file path to the visual display page that is
              currently being made the fit details table and the
              see also link
    :rtype : tuple(str, str)
    """

    # Group specific path and other misc stuff

    support_pages_dir = os.path.join(results_dir, group_name, "support_pages")
    if not os.path.exists(support_pages_dir):
        os.makedirs(support_pages_dir)

    file_name = (group_name + '_' + problem_name + '_' + str(count)).lower()
    file_path = os.path.join(support_pages_dir, file_name)

    return support_pages_dir, file_path


def get_figure_paths(support_pages_dir, problem_name, count):
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

    figures_dir = os.path.join(support_pages_dir, "figures")
    figure_fits = os.path.join(figures_dir, "Fit_for_" + problem_name +
                               "_" + str(count) + ".png")
    figure_strt = os.path.join(figures_dir, "start_for_" + problem_name +
                               "_" + str(count) + ".png")

    # If OS is Windows, then need to add prefix 'file:///'
    if os.name == 'nt':
        figure_fits = 'file:///' + figure_fits
        figure_strt = 'file:///' + figure_strt

    return figure_fits, figure_strt
