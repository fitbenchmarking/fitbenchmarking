"""
Functions that creates the tables and the visual display pages.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import logging
import os
import pandas as pd
from fitbenchmarking.utils.logging_setup import logger
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
    comparison_mode = software_options.get('comparison_mode', None)

    if comparison_mode is None:
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

    acc_tbl, acc_norm_tbl, acc_combined_table, \
        runtime_tbl, runtime_norm_tbl, runtime_combined_table \
        = generate_tables(results_per_test, minimizers, linked_problems)

    def colour_scheme(s):
        '''
        highlight the maximum in a Series yellow.
        '''
        is_max = s == s.min()
        return ['background-color: white' if v else '' for v in is_max]

    acc_norm_tbl = acc_norm_tbl.style.apply(colour_scheme, axis=1)
    html = acc_norm_tbl.render()

    save_tables(tables_dir, html, use_errors, group_name,
                FILENAME_SUFFIX_ACCURACY)
    save_tables(tables_dir, html, use_errors, group_name,
                FILENAME_SUFFIX_RUNTIME)

    # Shut down logging at end of run
    logging.shutdown()


def generate_tables(results_per_test, minimizers, linked_problems):
    """
    Generates accuracy and runtime tables, with both normalised and absolute results, and summary tables.

    @param results_per_test :: results nested array of objects
    @param minimizers :: array with minimizer names

    @returns :: data and summary tables of the results as np arrays
    """
    prev_name = ''
    count = 1
    acc_results_dict = OrderedDict()
    time_results_dict = OrderedDict()
    template = '<a target="_blank" href="{0}">{1}</a>'
    for test_idx, prob_results in enumerate(results_per_test):
        name = results_per_test[test_idx][0].problem.name
        if name == prev_name:
            count += 1
        else:
            count = 1
        prev_name = name
        prob_name = name + ' ' + str(count)

        name, url = linked_problems[test_idx].split('<')
        linked_name = template.format(url.split('>')[0], prob_name)

        acc_results_dict[linked_name] = [result.chi_sq for result in results_per_test[test_idx]]
        time_results_dict[prob_name] = [result.runtime for result in results_per_test[test_idx]]

    acc_tbl, acc_norm_tbl, acc_combined_table = create_tables(
        acc_results_dict,
        minimizers)
    runtime_tbl, runtime_norm_tbl, runtime_combined_table = create_tables(
        time_results_dict,
        minimizers)

    return acc_tbl, acc_norm_tbl, acc_combined_table, runtime_tbl, runtime_norm_tbl, runtime_combined_table


def create_tables(table_data, minimizers):
    """
    Generates pandas tables.

    :param table_data :: dictionary containing results
    :type group_name :: dict
    :param table_data :: list of minimizers (column headers)
    :type group_name :: list


    :return :: tuple(tbl, tbl_norm, tbl_combined) array of fitting results for
                the problem group and the path to the results directory
    :rtype :: (pandas DataFrame, pandas DataFrame, pandas DataFrame)
    """

    tbl = pd.DataFrame.from_dict(table_data, orient='index')
    tbl.columns = minimizers

    tbl_norm = tbl.apply(lambda x: x / x.min(), axis=1)

    tbl_combined = tbl.copy()
    for i in tbl_combined.columns:
        tbl_combined[i] = tbl[i].map(str) + \
            ' (' + tbl_norm[i].map(str) + ')'

    return tbl, tbl_norm, tbl_combined


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
    values = {True: 'weighted', False: 'unweighted'}
    table_name = ('{group_name}_{metric_type}_{weighted}_table.html'
                  .format(weighted=values[use_errors],
                          metric_type=metric, group_name=group_name))
    file_name = os.path.join(tables_dir, table_name)
    with open(file_name, 'w') as f:
        f.write(table_data)
