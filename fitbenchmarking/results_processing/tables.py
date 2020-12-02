"""
Set up and build the results tables.
"""

from __future__ import (absolute_import, division, print_function)
import copy
from importlib import import_module
from inspect import getfile, getmembers, isabstract, isclass
import os
from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing.base_table import Table
from fitbenchmarking.utils.exceptions import UnknownTableError
from fitbenchmarking.utils.misc import get_css, get_js

ERROR_OPTIONS = {0: "Successfully converged",
                 1: "Software reported maximum number of iterations exceeded",
                 2: "Software run but didn't converge to solution",
                 3: "Software raised an exception"}

SORTED_TABLE_NAMES = ["compare", "acc", "runtime", "local_min"]


def create_results_tables(options, results, best_results, group_name,
                          group_dir, pp_locations, failed_problems,
                          unselected_minimzers):
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
    :param pp_locations: tuple containing the locations of the
                         performance profiles (acc then runtime)
    :type pp_locations: tuple(str,str)
    :param failed_problems: list of failed problems to be reported in the
                            html output
    :type failed_problems: list
    :params unselected_minimzers: Dictionary containing unselected minimizers
                                  based on the algorithm_type option
    :type unselected_minimzers: dict

    :return: filepaths to each table
             e.g {'acc': <acc-table-filename>, 'runtime': ...}
             and dictionary of table descriptions
    :rtype: tuple(dict, dict)
    """

    weighted_str = 'weighted' if options.use_errors else 'unweighted'

    table_names = {}
    description = {}
    for suffix in SORTED_TABLE_NAMES:
        if suffix in options.table_type:
            table_names[suffix] = '{0}_{1}_{2}_table.'.format(group_name,
                                                              suffix,
                                                              weighted_str)

            table, html_table, txt_table = generate_table(results,
                                                          best_results,
                                                          options,
                                                          group_dir,
                                                          pp_locations,
                                                          table_names[suffix],
                                                          suffix)

            table_title = table.table_title
            file_path = table.file_path

            description = table.get_description(description)

            table_format = None if suffix == 'local_min' \
                else description[options.comparison_mode]

            has_pp = table.has_pp

            pp_filenames = table.pp_filenames

            root = os.path.dirname(getfile(fitbenchmarking))
            template_dir = os.path.join(root, 'templates')
            css = get_css(options, group_dir)
            js = get_js(options, group_dir)
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("table_template.html")
            html_output_file = file_path + 'html'
            txt_output_file = file_path + 'txt'

            with open(txt_output_file, "w") as f:
                f.write(txt_table)
            failed_minimzers = sum(list(unselected_minimzers.values()), [])
            report_failed_min = failed_minimzers != []

            with open(html_output_file, "w", encoding="utf-8") as f:
                f.write(
                    template.render(css_style_sheet=css['main'],
                                    custom_style=css['custom'],
                                    table_style=css['table'],
                                    mathjax=js['mathjax'],
                                    table_description=description[suffix],
                                    table_format=table_format,
                                    result_name=table_title,
                                    has_pp=has_pp,
                                    pp_filenames=pp_filenames,
                                    table=html_table,
                                    error_message=ERROR_OPTIONS,
                                    failed_problems=failed_problems,
                                    unselected_minimzers=unselected_minimzers,
                                    algorithm_type=options.algorithm_type,
                                    report_failed_min=report_failed_min))

    return table_names, description


def load_table(table):
    """
    Create and return table object.

    :param table: The name of the table to create a table for
    :type table: string

    :return: Table class for the problem
    :rtype: fitbenchmarking/results_processing/tables.Table subclass
    """

    module_name = '{}_table'.format(table.lower())

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise UnknownTableError('Given table option {} '
                                'was not found: {}'.format(table, e))

    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Table)
                                            and m is not Table))
    return classes[0][1]


def generate_table(results, best_results, options, group_dir,
                   pp_locations, table_name, suffix):
    """
    Generate html/txt tables.

    :param results: results nested array of objects
    :type results: list of list of
                   fitbenchmarking.utils.fitbm_result.FittingResult
    :param best_results: best result for each problem
    :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param group_dir: path to the directory where group results should be
                      stored
    :type group_dir: str
    :param pp_locations: tuple containing the locations of the
                         performance profiles (acc then runtime)
    :type pp_locations: tuple(str,str)
    :param table_name: name of the table
    :type table_name: str
    :param suffix: table suffix
    :type suffix: str


    :return: Table object, HTML string of table and text string of table.
    :rtype: tuple(Table object, str, str)
    """
    table_module = load_table(suffix)
    table = table_module(results, best_results,
                         options, group_dir,
                         pp_locations, table_name)

    results_dict = table.create_results_dict()

    disp_results = table.get_values(results_dict)
    error = table.get_error(results_dict)
    links = table.get_links(results_dict)
    colour = table.get_colour(disp_results)
    str_results = table.display_str(disp_results)

    pandas_html = table.create_pandas_data_frame(str_results)
    pandas_txt = copy.copy(pandas_html)

    html_table = table.to_html(pandas_html, colour, links, error)
    txt_table = table.to_txt(pandas_txt, error)
    return table, html_table, txt_table
