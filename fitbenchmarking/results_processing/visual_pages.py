"""
Set up and build the visual display pages for various types of problems.
"""

from __future__ import (absolute_import, division, print_function)

from jinja2 import Environment, FileSystemLoader
import os


def create_visual_pages(results_per_test, group_name, support_pages_dir,
                        options):
    """
    Iterate through problem results and create a visual display html page for
    each.

    :param results_per_test : results object
    :type results_per_test : list[list[list]]
    :param group_name : name of the problem group
    :type group_name : str
    :param support_pages_dir : directory in which the results are saved
    :type support_pages_dir : str
    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options
    """

    name_count = {}
    for prob_result in results_per_test:
        name = prob_result[0].problem.name
        name_count[name] = 1 + name_count.get(name, 0)
        count = name_count[name]

        create(prob_result,
               group_name,
               support_pages_dir,
               count,
               options)


def create(prob_results, group_name, support_pages_dir, count, options):
    """
    Creates a visual display page containing figures and other
    details about the fit for a problem.
    A link to the visual page is stored in the results object.

    :param prob_results : problem results objects containing results for
                          each minimizer and a certain fitting function
    :type prob_results : list[fitbenchmarking.utils.fitbm_result.FittingResult]
    :param group_name : name of the problem group
    :type group_name : str
    :param support_pages_dir : directory to store the support pages in
    :type support_pages_dir : str
    :param count : number of times a problem with the same name was
                   passed through this function
    :type count : int
    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options

    """

    for result in prob_results:
        prob_name = result.problem.name
        prob_name = prob_name.replace(',', '')
        prob_name = prob_name.replace(' ', '_')

        file_name = '{}_{}_{}_{}.html'.format(
            group_name, prob_name, count, result.minimizer).lower()
        file_path = os.path.join(support_pages_dir, file_name)

        fig_fit, fig_start = get_figure_paths(result, count)

        root = os.path.dirname(os.path.abspath(__file__))
        main_dir = os.path.dirname(root)
        html_page_dir = os.path.join(main_dir, "HTML_templates")
        env = Environment(loader=FileSystemLoader(html_page_dir))
        style_css = os.path.join(main_dir, 'HTML_templates/style_sheet.css')

        template = env.get_template("results_template.html")

        with open(file_path, 'w') as fh:
            fh.write(template.render(
                css_style_sheet=style_css,
                title=prob_name,
                equation=result.problem.equation,
                initial_guess=result.ini_function_params,
                minimiser=result.minimizer,
                make_plots=options.make_plots,
                initial_plot=fig_start,
                min_params=result.fin_function_params,
                fitted_plot=fig_fit))

        result.support_page_link = file_path


def get_figure_paths(result, count):
    """
    Get the paths to the figures used in the visual display page.

    :param result : THe result to get the figures for
    :type result : fitbenchmarking.utils.fitbm_result.FittingProblem
    :param count : number of times a problem with the same name was
                   passed through this function, consecutively
    :type count : int

    :return : the paths to the required figures
    :rtype : tuple(str, str)
    """

    if result.figure_link == '' and result.start_figure_link == '':
        message = 'Re-run with make_plots set to yes in the ini file to' \
            ' generate plots.'
        return message, message
    elif result.figure_link == '' or result.start_figure_link == '':
        raise ValueError('Missing links for plots.')

    figures_dir = "figures"
    figure_fits = os.path.join(figures_dir, result.figure_link)
    figure_strt = os.path.join(figures_dir, result.start_figure_link)

    # If OS is Windows, then need to add prefix 'file:///'
    if os.name == 'nt':
        figure_fits = 'file:///' + figure_fits
        figure_strt = 'file:///' + figure_strt

    return figure_fits, figure_strt
