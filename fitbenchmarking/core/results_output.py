"""
Functions that create the tables, support pages, figures, and indexes.
"""

from __future__ import (absolute_import, division, print_function)
import inspect
import os
from jinja2 import Environment, FileSystemLoader
from shutil import copy2

import fitbenchmarking
from fitbenchmarking.results_processing import performance_profiler, plots, \
    support_page, tables
from fitbenchmarking.utils import create_dirs
from fitbenchmarking.utils.misc import get_css, get_js


def save_results(options, results, group_name,
                 failed_problems, unselected_minimzers):
    """
    Create all results files and store them.
    Result files are plots, support pages, tables, and index pages.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: results nested array of objects
    :type results: list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult
    :param group_name: name of the problem group
    :type group_name: str
    :param failed_problems: list of failed problems to be reported in the
                            html output
    :type failed_problems: list
    :params unselected_minimzers: Dictionary containing unselected minimizers
                                  based on the algorithm_type option
    :type unselected_minimzers: dict

    :return: Path to directory of group results
    :rtype: str
    """
    group_dir, supp_dir, fig_dir, local_css_dir = \
                                        create_directories(options, group_name)

    # copy the template css files into a subfolder of results
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, 'templates')
    local_css_dir = os.path.join(options.results_dir, 'css')
    for css_file in ["main_style", "custom_style", "table_style"]:
        copy2(os.path.join(template_dir, css_file + ".css"), local_css_dir)
    best_results = preproccess_data(results)
    pp_locations = performance_profiler.profile(results, fig_dir)

    if options.make_plots:
        create_plots(options, results, best_results, fig_dir)
    support_page.create(options=options,
                        results_per_test=results,
                        group_name=group_name,
                        support_pages_dir=supp_dir)

    table_names, table_descriptions = \
        tables.create_results_tables(options,
                                     results,
                                     best_results,
                                     group_name,
                                     group_dir,
                                     pp_locations,
                                     failed_problems,
                                     unselected_minimzers)

    create_problem_level_index(options,
                               table_names,
                               group_name,
                               group_dir,
                               table_descriptions)

    return group_dir


def create_directories(options, group_name):
    """
    Create the directory structure ready to store the results

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param group_name: name of the problem group
    :type group_name: str
    :return: paths to the top level results, group results, support pages,
             and figures directories
    :rtype: (str, str, str, str)
    """
    results_dir = create_dirs.results(options.results_dir)
    group_dir = create_dirs.group_results(results_dir, group_name)
    support_dir = create_dirs.support_pages(group_dir)
    figures_dir = create_dirs.figures(support_dir)
    local_css_dir = create_dirs.css(options.results_dir)
    return group_dir, support_dir, figures_dir, local_css_dir


def preproccess_data(results_per_test):
    """
    Preprocess data into the right format for printing and find the best result
    for each problem

    :param results_per_test: results nested array of objects
    :type results_per_test: list of list of
                            fitbenchmarking.utils.fitbm_result.FittingResult

    :return: The best result for each problem
    :rtype: list of fitbenchmarking.utils.fitbm_result.FittingResult
    """
    output = []
    for results in results_per_test:
        best_result = min(results, key=lambda x: x.chi_sq)
        best_result.is_best_fit = True

        min_chi_sq = best_result.chi_sq
        min_runtime = min([r.runtime for r in results])
        for r in results:
            r.min_chi_sq = min_chi_sq
            r.min_runtime = min_runtime
        output.append(best_result)
    return output


def create_plots(options, results, best_results, figures_dir):
    """
    Create a plot for each result and store in the figures directory

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: results nested array of objects
    :type results: list of list of
                   fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param figures_dir: Path to directory to store the figures in
    :type figures_dir: str
    """
    for best, prob_result in zip(best_results, results):

        plot = plots.Plot(best_result=best,
                          options=options,
                          figures_dir=figures_dir)

        # Create a plot showing the initial guess and get filename
        initial_guess_path = plot.plot_initial_guess()

        # Setup best plot first
        # If none of the fits succeeded, params could be None
        # Otherwise, add the best fit to the plot
        if best.params is not None:
            plot_path = plot.plot_best(best.sanitised_min_name, best.params)
            best.figure_link = plot_path
        else:
            best.figure_error = 'Minimizer failed to produce any parameters'
        best.start_figure_link = initial_guess_path

        # For each result, if it succeeded, create a plot and add plot links to
        # the resuts object
        for result in prob_result:
            # Don't plot best again
            if not result.is_best_fit:
                if result.params is not None:
                    plot_path = plot.plot_fit(result.sanitised_min_name,
                                              result.params)
                    result.figure_link = plot_path
                else:
                    result.figure_error = 'Minimizer failed to produce any ' \
                        'parameters'
                result.start_figure_link = initial_guess_path


def create_problem_level_index(options, table_names, group_name,
                               group_dir, table_descriptions):
    """
    Generates problem level index page.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param table_names: list of table names
    :type table_names: list
    :param group_name: name of the problem group
    :type group_name: str
    :param group_dir: Path to the directory where the index should be stored
    :type group_dir: str
    :param table_descriptions: dictionary containing descriptions of the
                               tables and the comparison mode
    :type table_descriptions: dict
    """
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options,group_dir)
    js = get_js(options,group_dir)
    template = env.get_template("problem_index_page.html")
    output_file = os.path.join(group_dir, '{}_index.html'.format(group_name))
    links = [v + "html" for v in table_names.values()]
    names = table_names.keys()
    description = [table_descriptions[n] for n in names]
    index = table_descriptions[options.comparison_mode]
    with open(output_file, 'w', encoding="utf-8") as fh:
        fh.write(template.render(
            css_style_sheet=css['main'],
            custom_style=css['custom'],
            mathjax=js['mathjax'],
            group_name=group_name,
            index=index,
            table_type=names,
            links=links,
            description=description,
            zip=zip))
