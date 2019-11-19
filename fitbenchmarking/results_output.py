"""
Functions that creates the tables and the visual display pages.
"""

from __future__ import (absolute_import, division, print_function)

import logging

from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.resproc import numpy_restables
from fitbenchmarking.resproc import rst_table
from fitbenchmarking.resproc import visual_pages
from fitbenchmarking.utils import create_dirs

# Some naming conventions for the output files
FILENAME_SUFFIX_ACCURACY = 'acc'
FILENAME_SUFFIX_RUNTIME = 'runtime'
FILENAME_EXT_TXT = 'txt'
FILENAME_EXT_HTML = 'html'


def save_results_tables(options, results, group_name):
    """
    Saves the results of the fitting to html/rst tables.

    @param options :: options used in fitting
    @param results_per_test :: results nested array of objects
    @param group_name :: name of the problem group

    @returns :: html/rst tables with the fitting results
    """

    software = options.software
    if not isinstance(software, list):
        software = [software]
    minimizers = [options.minimizers[s] for s in software]
    minimizers = sum(minimizers, [])

    comparison_mode = options.comparison_mode

    results_dir = options.results_dir
    use_errors = options.use_errors
    colour_scale = options.colour_scale

    tables_dir = create_dirs.restables_dir(results_dir, group_name)
    linked_problems = \
        visual_pages.create_linked_probs(results, group_name, results_dir)

    acc_rankings, runtimes, _, _ = generate_tables(results, minimizers)

    acc_tbl = rst_table.create(columns_txt=minimizers,
                               rows_txt=linked_problems,
                               cells=acc_rankings,
                               comparison_type='accuracy',
                               comparison_dim='',
                               using_errors=use_errors,
                               color_scale=colour_scale,
                               comparison_mode=comparison_mode)

    runtime_tbl = rst_table.create(columns_txt=minimizers,
                                   rows_txt=linked_problems,
                                   cells=runtimes,
                                   comparison_type='runtime',
                                   comparison_dim='',
                                   using_errors=use_errors,
                                   color_scale=colour_scale,
                                   comparison_mode=comparison_mode)

    save_tables(tables_dir, acc_tbl, use_errors, group_name,
                FILENAME_SUFFIX_ACCURACY)
    save_tables(tables_dir, runtime_tbl, use_errors, group_name,
                FILENAME_SUFFIX_RUNTIME)

    # Shut down logging at end of run
    logging.shutdown()


def create_acc_tbl(minimizers, linked_problems, accuracy_tbl, use_errors,
                   color_scale, comparison_mode='abs'):
    """
    API function to create an accuracy table using the given parameters.
    For usage, see the expert example script.

    @param minimizers :: array of minimizers used in fitting
    @param linked_problems :: array of the problems that were fitted
    @param accuracy_tbl :: numpy array of the accuracy results
    @param using_errors :: boolean whether to use errors or not
    @param color_scale :: color scale for coloring the cells
    @param comparison_mode :: str to select between 'abs', 'rel', 'both' for
                              the style of comparison returned

    @returns :: rst table of the results
    """
    # Save accuracy table for this group of fit problems
    tbl_acc_indiv = rst_table.create(minimizers, linked_problems,
                                     accuracy_tbl,
                                     comparison_type='accuracy',
                                     comparison_dim='',
                                     using_errors=use_errors,
                                     color_scale=color_scale,
                                     comparison_mode=comparison_mode)

    return tbl_acc_indiv


def create_runtime_tbl(minimizers, linked_problems, runtime_tbl, use_errors,
                       color_scale, comparison_mode='abs'):
    """
    API function to create a runtime table using the given parameters.
    For usage, see the expert example script.

    @param minimizers :: array of minimizers used in fitting
    @param linked_problems :: array of the problems that were fitted
    @param runtime_tbl :: numpy array of the runtime results
    @param using_errors :: boolean whether to use errors or not
    @param color_scale :: color scale for coloring the cells
    @param comparison_mode :: str to select between 'abs', 'rel', 'both' for
                              the style of comparison returned

    @returns :: rst table of the results
    """
    # Save runtime table for this group of fit problems
    tbl_runtime_indiv = rst_table.create(minimizers, linked_problems,
                                         runtime_tbl,
                                         comparison_type='runtime',
                                         comparison_dim='',
                                         using_errors=use_errors,
                                         color_scale=color_scale,
                                         comparison_mode=comparison_mode)

    return tbl_runtime_indiv


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
