"""
Set up and build the support pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

import inspect
import os

from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.utils.misc import get_css


def create(results_per_test, group_name, support_pages_dir,
           options):
    """
    Iterate through problem results and create a support html page for
    each.

    :param results_per_test: results object
    :type results_per_test: list[list[list]]
    :param group_name: name of the problem group
    :type group_name: str
    :param support_pages_dir: directory in which the results are saved
    :type support_pages_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """

    for prob_result in results_per_test:

        create_prob_group(prob_result,
                          group_name,
                          support_pages_dir,
                          options)


def create_prob_group(prob_results, group_name, support_pages_dir,
                      options):
    """
    Creates a support page containing figures and other
    details about the fit for a problem.
    A link to the support page is stored in the results object.

    :param prob_results: problem results objects containing results for
                         each minimizer and a certain fitting function
    :type prob_results: list[fitbenchmarking.utils.fitbm_result.FittingResult]
    :param group_name: name of the problem group
    :type group_name: str
    :param support_pages_dir: directory to store the support pages in
    :type support_pages_dir: str
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """

    for result in prob_results:
        prob_name = result.sanitised_name

        file_name = '{}_{}_{}.html'.format(
            group_name, prob_name, result.sanitised_min_name)
        file_name = file_name.lower()
        file_path = os.path.join(support_pages_dir, file_name)

        # Bool for print message/insert image
        fit_success = init_success = options.make_plots

        if options.make_plots:
            fig_fit, fig_start = get_figure_paths(result)
            if fig_fit == '':
                fig_fit = result.figure_error
                fit_success = False
            if fig_start == '':
                fig_start = result.figure_error
                init_success = False
        else:
            fig_fit = fig_start = 'Re-run with make_plots set to yes in the ' \
                                  'ini file to generate plots.'

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        template_dir = os.path.join(root, "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        css = get_css(options, support_pages_dir)
        template = env.get_template("support_page_template.html")

        with open(file_path, 'w') as fh:
            fh.write(template.render(
                css_style_sheet=css['main'],
                table_style=css['table'],
                custom_style=css['custom'],
                title=result.name,
                equation=result.problem.equation,
                initial_guess=result.ini_function_params,
                minimizer=result.minimizer,
                is_best_fit=result.is_best_fit,
                initial_plot_available=init_success,
                initial_plot=fig_start,
                min_params=result.fin_function_params,
                fitted_plot_available=fit_success,
                fitted_plot=fig_fit))

        result.support_page_link = os.path.relpath(file_path)


def get_figure_paths(result):
    """
    Get the paths to the figures used in the support page.

    :param result: The result to get the figures for
    :type result: fitbenchmarking.utils.fitbm_result.FittingProblem

    :return: the paths to the required figures
    :rtype: tuple(str, str)
    """

    figures_dir = "figures"

    output = []
    for link in [result.figure_link, result.start_figure_link]:
        if link == '':
            output.append('')
        else:
            path = os.path.join(figures_dir, link)
            output.append(path)

    return output[0], output[1]
