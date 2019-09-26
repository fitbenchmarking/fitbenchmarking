"""
Functions that creates the tables and the visual display pages.
"""

from __future__ import (absolute_import, division, print_function)

import logging

from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.resproc import numpy_restables
from fitbenchmarking.resproc import rst_table
from fitbenchmarking.resproc import visual_pages
from fitbenchmarking.utils import create_dirs, options, misc

# Some naming conventions for the output files
FILENAME_SUFFIX_ACCURACY = 'acc'
FILENAME_SUFFIX_RUNTIME = 'runtime'
FILENAME_EXT_TXT = 'txt'
FILENAME_EXT_HTML = 'html'


def save_results_tables(software_options, results_per_test, group_name,
                        use_errors, color_scale=None, results_dir=None):
    """
    Saves the results of the fitting to html/rst tables.

    @param software_options :: dictionary containing software used in fitting the problem, list of minimizers and location of json file contain minimizers
    @param minimizers :: array with minimizer names
    @param results_per_test :: results nested array of objects
    @param group_name :: name of the problem group
    @param use_errors :: bool whether to use errors or not
    @param color_scale :: color the html table
    @param results_dir :: directory in which the results are saved

    @returns :: html/rst tables with the fitting results
    """

    minimizers, software = misc.get_minimizers(software_options)
    comparison_type = software_options.get('comparison_type', None)

    if comparison_type is None:
        if 'options_file' in software_options:
            options_file = software_options['options_file']
            comparison_mode = options.get_option(options_file=options_file,
                                                 option='comparison_mode')
        else:
            comparison_mode = options.get_option(option='comparison_mode')

        if comparison_mode is None:
            comparison_mode = 'both'

    if isinstance(software, list):
        minimizers = sum(minimizers, [])

    tables_dir = create_dirs.restables_dir(results_dir, group_name)
    linked_problems = \
        visual_pages.create_linked_probs(results_per_test, group_name, results_dir)

    acc_rankings, runtimes, _, _ = generate_tables(results_per_test, minimizers)

    acc_tbl = rst_table.create(columns_txt=minimizers,
                               rows_txt=linked_problems,
                               cells=acc_rankings,
                               comparison_type='accuracy',
                               comparison_dim='',
                               using_errors=use_errors,
                               color_scale=color_scale,
                               comparison_mode=comparison_mode)

    runtime_tbl = rst_table.create(columns_txt=minimizers,
                                   rows_txt=linked_problems,
                                   cells=runtimes,
                                   comparison_type='runtime',
                                   comparison_dim='',
                                   using_errors=use_errors,
                                   color_scale=color_scale,
                                   comparison_mode=comparison_mode)

    save_tables(tables_dir, acc_tbl, use_errors, group_name,
                FILENAME_SUFFIX_ACCURACY)
    save_tables(tables_dir, runtime_tbl, use_errors, group_name,
                FILENAME_SUFFIX_RUNTIME)

    # Shut down logging at end of run
    logging.shutdown()


def generate_tables(results_per_test, minimizers):
    """
    Generates accuracy and runtime tables, with both normalised and absolute results, and summary tables.

    @param results_per_test :: results nested array of objects
    @param minimizers :: array with minimizer names

    @returns :: data and summary tables of the results as np arrays
    """

    accuracy_tbl, runtime_tbl = \
        numpy_restables.create_accuracy_runtime_tbls(results_per_test, minimizers)

    norm_acc_rankings, norm_runtimes = \
        numpy_restables.create_norm_tbls(accuracy_tbl, runtime_tbl)

    accuracy_tbl, runtime_tbl = numpy_restables.create_combined_tbls(abs_accuracy=accuracy_tbl,
                                                                     rel_accuracy=norm_acc_rankings,
                                                                     abs_runtime=runtime_tbl,
                                                                     rel_runtime=norm_runtimes)

    sum_cells_acc, sum_cells_runtime = \
        numpy_restables.create_summary_tbls(accuracy_tbl, runtime_tbl)

    return accuracy_tbl, runtime_tbl, sum_cells_acc, sum_cells_runtime


def save_tables(tables_dir, table_data, use_errors, group_name, metric):
    """
    Helper function that saves the rst table both to html and to text.

    @param tables_dir :: the directory in which the tables are saved
    @param table_data :: the results table, in rst
    @param use_errors :: bool whether errors were used or not
    @param group_name :: name of the problem group
    @param metric :: whether it is an accuracy or runtime table

    @returns :: tables saved to both html and txt.
    """

    rst_table.save_table_to_file(results_dir=tables_dir, table_data=table_data,
                                 use_errors=use_errors, group_name=group_name,
                                 metric_type=metric,
                                 file_extension=FILENAME_EXT_TXT)
    rst_table.save_table_to_file(results_dir=tables_dir, table_data=table_data,
                                 use_errors=use_errors, group_name=group_name,
                                 metric_type=metric,
                                 file_extension=FILENAME_EXT_HTML)
