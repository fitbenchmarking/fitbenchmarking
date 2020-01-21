"""
Functions that create the tables, support pages, figures, and indexes.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import copy
import inspect
import os

from jinja2 import Environment, FileSystemLoader
import pandas as pd

import fitbenchmarking
from fitbenchmarking.results_processing import plots, visual_pages
from fitbenchmarking.utils import create_dirs

error_options = {0: "Successfully converged",
                 1: "Software reported maximum number of iterations exceeded",
                 2: "Software run but didn't converge to solution",
                 3: "Software raised an exception"}


def save_results(options, results, group_name):
    """
    Create all results files and store them.
    Result files are plots, visual pages, tables, and index pages.

    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options
    :param results : results nested array of objects
    :type results : list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult
    :param group_name : name of the problem group
    :type group_name : str

    :return: Path to directory of group results
    :rtype: str
    """
    _, group_dir, supp_dir, fig_dir = create_directories(options, group_name)
    best_results = preproccess_data(results)
    if options.make_plots:
        create_plots(options, results, best_results, group_name, fig_dir)
    visual_pages.create_visual_pages(options=options,
                                     results_per_test=results,
                                     group_name=group_name,
                                     support_pages_dir=supp_dir)
    table_names = create_results_tables(options,
                                        results,
                                        best_results,
                                        group_name,
                                        group_dir)
    create_problem_level_index(options, table_names, group_name, group_dir)

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
    return results_dir, group_dir, support_dir, figures_dir


def preproccess_data(results_per_test):
    """
    Preprocess data into the right format for printing and find the best result
    for each problem

    :param results_per_test: results nested array of objects
    :type results_per_test : list of list of
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
            r.set_colour_scale()
        output.append(best_result)
    return output


def create_plots(options, results, best_results, group_name, figures_dir):
    """
    Create a plot for each result and store in the figures directory

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: results nested array of objects
    :type results : list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param group_name: name of he problem group
    :type group_name: str
    :param figures_dir: Path to directory to store the figures in
    :type figures_dir: str
    """
    name_count = {}
    for best, prob_result in zip(best_results, results):
        name = best.problem.sanitised_name
        name_count[name] = 1 + name_count.get(name, 0)
        count = name_count[name]

        plot = plots.Plot(problem=best.problem,
                          options=options,
                          count=count,
                          figures_dir=figures_dir)

        # Create a plot showing the initial guess and get filename
        initial_guess_path = plot.plot_initial_guess()

        # Setup best plot first
        # If none of the fits succeeded, params could be None
        # Otherwise, add the best fit to the plot
        if best.params is not None:
            plot_path = plot.plot_best(best.minimizer, best.params)
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
                    plot_path = plot.plot_fit(result.minimizer, result.params)
                    result.figure_link = plot_path
                else:
                    result.figure_error = 'Minimizer failed to produce any ' \
                        'parameters'
                result.start_figure_link = initial_guess_path


def create_results_tables(options, results, best_results, group_name,
                          group_dir):
    """
    Saves the results of the fitting to html/txt tables.

    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options
    :param results : results nested array of objects
    :type results : list of list of
                    fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param group_name : name of the problem group
    :type group_name : str
    :param group_dir : path to the directory where group results should be
                       stored
    :type group_dir : str

    :return: filepaths to each table
             e.g {'acc': <acc-table-filename>, 'runtime': ...}
    :rtype: dict
    """
    weighted_str = 'weighted' if options.use_errors else 'unweighted'

    table_names = OrderedDict()
    for suffix in options.table_type:
        table_names[suffix] = '{0}_{1}_{2}_table.'.format(group_name,
                                                          suffix,
                                                          weighted_str)
    generate_tables(results, best_results, table_names, options.table_type,
                    group_dir)
    return table_names


def generate_tables(results_per_test, best_results, table_names, table_suffix,
                    group_dir):
    """
    Generates accuracy, runtime, and combined accuracy and runtime tables, with
    both normalised and absolute results in both txt and html.

    :param results_per_test : results nested array of objects
    :type results_per_test : list of list of
                             fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param table_names : list of table names
    :type table_names : list
    :param table_suffix : set output to be runtime or accuracy table
    :type table_suffix : str
    :param group_dir: path to group results directory
    :type group_dir: str
    """
    table_titles = ["FitBenchmarking: {0} table".format(name)
                    for name in table_suffix]
    results_dict = create_results_dict(results_per_test)
    table = create_pandas_dataframe(results_dict, table_suffix)
    render_pandas_dataframe(table, best_results, table_names, table_titles,
                            group_dir)


def create_results_dict(results_per_test):
    """
    Generates a dictionary used to create HTML and txt tables.

    :param results_per_test : results nested array of objects
    :type results_per_test : list of list of
                             fitbenchmarking.utils.fitbm_result.FittingResult

    :return : A dictionary of results objects
    :rtype : dict
    """

    results = OrderedDict()

    name_count = {}
    for prob_results in results_per_test:
        name = prob_results[0].problem.sanitised_name
        name_count[name] = 1 + name_count.get(name, 0)
        count = name_count[name]

        prob_name = name + ' ' + str(count)
        results[prob_name] = prob_results
    return results


def create_pandas_dataframe(table_data, table_suffix):
    """
    Generates pandas data frame.

    :param table_data : dictionary containing results, i.e.,
                            {'prob1': [result1, result2, ...],
                             'prob2': [result1, result2, ...], ...}
    :type table_data : dict
    :param table_suffix : set output to be runtime or accuracy table
    :type table_suffix : list


    :return : dict(tbl, tbl_norm, tbl_combined) dictionary of
               pandas DataFrames containing results.
    :rtype : dict{pandas DataFrame, pandas DataFrame}
    """

    # This function is only used in the mapping, hence, it is defined here.
    def select_table(value, table_suffix):
        '''
        Selects either accuracy or runtime table.
        '''
        value.table_type = table_suffix
        value = copy.copy(value)
        return value

    tbl = pd.DataFrame.from_dict(table_data, orient='index')
    # Get minimizers from first row of objects to use as columns
    tbl.columns = [r.minimizer for r in tbl.iloc[0]]
    results = OrderedDict()
    for suffix in table_suffix:
        results[suffix] = tbl.applymap(lambda x: select_table(x, suffix))
    return results


def render_pandas_dataframe(table_dict, best_results, table_names,
                            table_title, group_dir):
    """
    Generates html and txt page from pandas dataframes.

    :param table_dict : dictionary of DataFrame of the results
    :type table_dict : dict(pandas DataFrame, ...)
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param table_names : list of table names
    :type table_names : list
    :param table_title : list of table titles
    :type table_title : list
    :param group_dir: path to the group results directory
    :type group_dir: str
    """

    # Define functions that are used in calls to map over dataframes
    def colour_highlight(value):
        '''
        Colour mapping for visualisation of table
        '''
        colour = value.colour
        if isinstance(colour, list):
            # Use 4 colours in gradient to make gradient only change in centre
            # of cell
            colour_output = \
                'background-image: linear-gradient({0},{0},{1},{1})'.format(
                    colour[0], colour[1])
        else:
            colour_output = 'background-color: {0}'.format(colour)
        return colour_output

    def enable_link(result):
        '''
        Enable HTML links in values

        Note: Due to the way applymap works in DataFrames, this cannot make a
        change based on the state of the value

        :param result: The result object to update
        :type result: fitbenchmaring.utils.fitbm_result.FittingResult

        :return: The same result object after updating
        :rtype: fitbenchmarking.utils.fitbm_result.FittingResult
        '''
        result.relative_dir = group_dir
        result.html_print = True
        return result

    for name, title, table in zip(table_names.items(), table_title,
                                  table_dict.values()):

        file_path = os.path.join(group_dir, name[1])
        with open(file_path + 'txt', "w") as f:
            f.write(table.to_string())

        # Update table indexes to link to the best support page
        index = []
        for b, i in zip(best_results, table.index):
            rel_path = os.path.relpath(path=b.support_page_link,
                                       start=group_dir)
            index.append('<a href="{0}">{1}</a>'.format(rel_path, i))
        table.index = index

        # Update table values to point to individual support pages
        table.applymap(enable_link)

        # Set colour on each cell and add title
        table_style = table.style.applymap(colour_highlight)
        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        html_page_dir = os.path.join(root, 'HTML_templates')
        style_css = os.path.join(html_page_dir, 'style_sheet.css')
        env = Environment(loader=FileSystemLoader(html_page_dir))
        template = env.get_template("table_template.html")
        output_file = file_path + 'html'

        with open(output_file, "w") as f:
            f.write(template.render(css_style_sheet=style_css,
                                    result_name=title,
                                    table=table_style.render(),
                                    error_message=error_options))


def create_problem_level_index(options, table_names, group_name, group_dir):
    """
    Generates problem level index page.

    :param options : The options used in the fitting problem and plotting
    :type options : fitbenchmarking.utils.options.Options
    :param table_names : list of table names
    :type table_names : list
    :param group_name : name of the problem group
    :type group_name : str
    :param group_dir : Path to the directory where the index should be stored
    :type group_dir : str

    """
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    html_page_dir = os.path.join(root, 'HTML_templates')
    env = Environment(loader=FileSystemLoader(html_page_dir))
    style_css = os.path.join(html_page_dir, 'style_sheet.css')
    template = env.get_template("problem_index_page.html")

    output_file = os.path.join(group_dir, '{}_index.html'.format(group_name))
    with open(output_file, 'w') as fh:
        fh.write(template.render(
            css_style_sheet=style_css,
            group_name=group_name,
            acc="acc" in options.table_type,
            alink=table_names['acc'] +
                "html" if 'acc' in table_names else 0,
            runtime="runtime" in options.table_type,
            rlink=table_names['runtime'] +
                "html" if 'runtime' in table_names else 0,
            compare="compare" in options.table_type,
            clink=table_names['compare'] +
                "html" if 'compare' in table_names else 0))
