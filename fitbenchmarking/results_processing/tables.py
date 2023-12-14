"""
Set up and build the results tables.
"""
import os
from importlib import import_module
from inspect import getfile, getmembers, isabstract, isclass

from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.results_processing.base_table import Table
from fitbenchmarking.utils.exceptions import (IncompatibleTableError,
                                              UnknownTableError)
from fitbenchmarking.utils.log import get_logger
from fitbenchmarking.utils.misc import get_css, get_js

LOGGER = get_logger()

ERROR_OPTIONS = {0: "Successfully converged",
                 1: "Software reported maximum number of iterations exceeded",
                 2: "Software run but didn't converge to solution",
                 3: "Software raised an exception",
                 4: "Solver doesn't support bounded problems",
                 5: "Solution doesn't respect parameter bounds",
                 6: "Solver has exceeded maximum allowed runtime",
                 7: "Validation of the provided options failed"}

SORTED_TABLE_NAMES = ["compare", "acc", "runtime", "local_min", 'emissions']


def create_results_tables(options, results, best_results, group_dir, fig_dir,
                          pp_locations, failed_problems, unselected_minimzers):
    """
    Saves the results of the fitting to html/csv tables.

    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param results: Results grouped by row and category (for colouring)
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    :param best_results: The best results from each row/category
    :type best_results: dict[str, dict[str, utils.fitbm_result.FittingResult]]
    :param group_dir: path to the directory where group results should be
                      stored
    :type group_dir: str
    :param fig_dir: path to the directory where figures should be stored
    :type fig_dir: str
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

    table_names = {}
    description = {}
    for suffix in SORTED_TABLE_NAMES:
        if suffix in options.table_type:

            table_names[suffix] = f'{suffix}_table.'

            try:
                table, html, csv_table, cbar = \
                    generate_table(results=results,
                                   best_results=best_results,
                                   options=options,
                                   group_dir=group_dir,
                                   fig_dir=fig_dir,
                                   pp_locations=pp_locations,
                                   table_name=table_names[suffix],
                                   suffix=suffix)
            except IncompatibleTableError as excp:
                LOGGER.warning(str(excp))
                del table_names[suffix]
                continue

            description.update(table.get_description())

            if suffix == 'local_min':
                table_format = description['local_min_mode']
            else:
                table_format = description[options.comparison_mode]

            if suffix in ['runtime', 'compare']:
                description[suffix] = description[suffix].format(
                    runtime_metric=options.runtime_metric)

            root = os.path.dirname(getfile(fitbenchmarking))
            template_dir = os.path.join(root, 'templates')

            css = get_css(options, group_dir)
            js = get_js(options, group_dir)

            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template("table_template.html")

            run_name = f"{options.run_name}: " if options.run_name else ""

            with open(f'{table.file_path}csv', "w") as f:
                f.write(csv_table)

            report_failed_min = \
                any(minimizers for minimizers in unselected_minimzers.values())

            if len(table.pp_filenames) == 1:
                pp_index = ['1']
            elif len(table.pp_filenames) == 2:
                pp_index = ['1', '2']
            else:
                # This error message is necessary because pp_index is used in
                # the table template to display the performance profiles
                raise ValueError('Displaying more than two profiles in a '
                                 'single page is not possible yet.')

            with open(f'{table.file_path}html', "w", encoding="utf-8") as f:
                f.write(
                    template.render(css_style_sheet=css['main'],
                                    custom_style=css['custom'],
                                    dropdown_style=css['dropdown'],
                                    table_style=css['table'],
                                    dropdown_js=js['dropdown'],
                                    mathjax=js['mathjax'],
                                    table_js=js['table'],
                                    table=html['table'],
                                    problem_dropdown=html['problem_dropdown'],
                                    minimizer_dropdown=html['minim_dropdown'],
                                    probsize_checkbox=html['probsize_checkb'],
                                    table_description=description[suffix],
                                    table_format=table_format,
                                    result_name=table.table_title,
                                    has_pp=table.has_pp,
                                    pp_filenames=table.pp_filenames,
                                    pp_dash_urls=table.pp_dash_urls,
                                    zipped_paths=zip(table.pp_filenames,
                                                     table.pp_dash_urls,
                                                     pp_index),
                                    cbar=cbar,
                                    run_name=run_name,
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

    module_name = f'{table.lower()}_table'

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        raise UnknownTableError(f'Given table option {table} '
                                f'was not found: {e}') from e

    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Table)
                                            and m is not Table))
    return classes[0][1]


def generate_table(results, best_results, options, group_dir, fig_dir,
                   pp_locations, table_name, suffix):
    """
    Generate html/csv tables.

    :param results: Results grouped by row and category (for colouring)
    :type results: dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
    :param best_results: The best results from each row/category
    :type best_results: dict[str, dict[str, utils.fitbm_result.FittingResult]]
    :param options: The options used in the fitting problem and plotting
    :type options: fitbenchmarking.utils.options.Options
    :param group_dir: path to the directory where group results should be
                      stored
    :type group_dir: str
    :param fig_dir: path to the directory where figures should be stored
    :type fig_dir: str
    :param pp_locations: tuple containing the locations of the
                         performance profiles (acc then runtime)
    :type pp_locations: tuple(str,str)
    :param table_name: name of the table
    :type table_name: str
    :param suffix: table suffix
    :type suffix: str

    :return: (Table object, Dict of HTML strings for table and dropdowns,
    text string of table, path to colourbar)
    :rtype: tuple(Table object, dict{str: str}, str, str)
    """
    table_module = load_table(suffix)
    table = table_module(results, best_results, options, group_dir,
                         pp_locations, table_name)

    html_table = table.to_html()
    csv_table = table.to_csv_file()
    cbar = table.save_colourbar(fig_dir)

    problem_dropdown_html = table.problem_dropdown_html()
    minimizer_dropdown_html = table.minimizer_dropdown_html()
    probsize_checkbox_html = table.probsize_checkbox_html()

    html_dict = {
        'table': html_table,
        'problem_dropdown': problem_dropdown_html,
        'minim_dropdown': minimizer_dropdown_html,
        'probsize_checkb': probsize_checkbox_html
    }

    return table, html_dict, csv_table, cbar
