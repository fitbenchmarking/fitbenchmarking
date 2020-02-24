"""
Set up and build the results tables.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import copy
import inspect
from jinja2 import Environment, FileSystemLoader
import os
import pandas as pd

import fitbenchmarking

ERROR_OPTIONS = {0: "Successfully converged",
                 1: "Software reported maximum number of iterations exceeded",
                 2: "Software run but didn't converge to solution",
                 3: "Software raised an exception"}

SORTED_TABLE_NAMES = ["compare", "acc", "runtime", "local_min"]


def create_results_tables(options, results, best_results, group_name,
                          group_dir, table_descriptions):
    """
    Saves the results of the fitting to html/txt tables.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: results nested array of objects
    :type results: list of list of
                   fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param group_name: name of the problem group
    :type group_name: str
    :param group_dir: path to the directory where group results should be
                      stored
    :type group_dir: str
    :param table_descriptions: dictionary containing descriptions of the
                               tables and the comparison mode
    :type table_descriptions: dict

    :return: filepaths to each table
             e.g {'acc': <acc-table-filename>, 'runtime': ...}
    :rtype: dict
    """
    weighted_str = 'weighted' if options.use_errors else 'unweighted'

    table_type = []
    table_names = OrderedDict()
    for suffix in SORTED_TABLE_NAMES:
        if suffix in options.table_type:
            table_type.append(suffix)
            table_names[suffix] = '{0}_{1}_{2}_table.'.format(group_name,
                                                              suffix,
                                                              weighted_str)
    generate_tables(results, best_results, table_names, table_type,
                    group_dir, table_descriptions, options)
    return table_names


def generate_tables(results_per_test, best_results, table_names, table_suffix,
                    group_dir, table_descriptions, options):
    """
    Generates accuracy, runtime, and combined accuracy and runtime tables, with
    both normalised and absolute results in both txt and html.

    :param results_per_test: results nested array of objects
    :type results_per_test: list of list of
                            fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param table_names: list of table names
    :type table_names: list
    :param table_suffix: set output to be runtime or accuracy table
    :type table_suffix: str
    :param group_dir: path to group results directory
    :type group_dir: str
    :param table_descriptions: dictionary containing descriptions of the
                               tables and the comparison mode
    :type table_descriptions: dict
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    """
    table_titles = ["FitBenchmarking: {0} table".format(name)
                    for name in table_suffix]
    results_dict = create_results_dict(results_per_test)
    table = create_pandas_dataframe(results_dict, table_suffix)
    render_pandas_dataframe(table, best_results, table_names, table_titles,
                            group_dir, table_descriptions, options)


def create_results_dict(results_per_test):
    """
    Generates a dictionary used to create HTML and txt tables.

    :param results_per_test: results nested array of objects
    :type results_per_test: list of list of
                             fitbenchmarking.utils.fitbm_result.FittingResult

    :return: Results objects
    :rtype: dict
    """

    results = OrderedDict()

    name_count = {}
    for prob_results in results_per_test:
        name = prob_results[0].problem.name
        name_count[name] = 1 + name_count.get(name, 0)
        count = name_count[name]

        prob_name = name + ' ' + str(count)
        results[prob_name] = prob_results
    return results


def create_pandas_dataframe(table_data, table_suffix):
    """
    Generates pandas data frame.

    :param table_data: dictionary containing results, i.e.,
                       {'prob1': [result1, result2, ...],
                        'prob2': [result1, result2, ...], ...}
    :type table_data: dict
    :param table_suffix: set output to be runtime or accuracy table
    :type table_suffix: list

    :return: dict(tbl, tbl_norm, tbl_combined) dictionary of
             pandas DataFrames containing results.
    :rtype: dict{pandas DataFrame, pandas DataFrame}
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
                            table_title, group_dir, table_descriptions,
                            options):
    """
    Generates html and txt page from pandas dataframes,
    and writes them to files.

    :param table_dict: dictionary of DataFrame of the results
    :type table_dict: dict(pandas DataFrame, ...)
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param table_names: list of table names
    :type table_names: list
    :param table_title: list of table titles
    :type table_title: list
    :param group_dir: path to the group results directory
    :type group_dir: str
    :param table_descriptions: dictionary containing descriptions of the
                               tables and the comparison mode
    :type table_descriptions: dict
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
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
        description = table_descriptions[name[0]]

        table_format = None if name[0] == 'local_min' \
            else table_descriptions[options.comparison_mode]

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

        # add performance profile information
        has_pp = False
        print("title = {}".format(name[0]))
        if name[0] in 'acc':
            has_pp = True
        elif name[0] in 'runtime':
            has_pp = True
            
        pp_location = ''
        
        # Set colour on each cell and add title
        table_style = table.style.applymap(colour_highlight)
        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        template_dir = os.path.join(root, 'templates')
        style_css = os.path.join(template_dir, 'main_style.css')
        table_css = os.path.join(template_dir, 'table_style.css')
        custom_style = os.path.join(template_dir, 'custom_style.css')
        maths_style = os.path.join(template_dir, 'math_style.css')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("table_template.html")
        output_file = file_path + 'html'

        with open(output_file, "w") as f:
            f.write(template.render(css_style_sheet=style_css,
                                    custom_style=custom_style,
                                    table_style=table_css,
                                    maths_style=maths_style,
                                    table_description=description,
                                    table_format=table_format,
                                    result_name=title,
                                    has_pp=has_pp,
                                    pp_location=pp_location,
                                    table=table_style.render(),
                                    error_message=ERROR_OPTIONS))
