"""
Functions that creates the tables and the visual display pages.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import logging
import numpy as np
import os
import pandas as pd
import pytablewriter
import re


from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.resproc import visual_pages
from fitbenchmarking.utils import create_dirs, options, misc

# Some naming conventions for the output files
FILENAME_SUFFIX_ACCURACY = 'acc'
FILENAME_SUFFIX_RUNTIME = 'runtime'
FILENAME_EXT_TXT = 'txt'
FILENAME_EXT_HTML = 'html'

HTML_COLUR_SCALE = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']


def save_results_tables(software_options, results_per_test, group_name,
                        use_errors, color_scale=None, results_dir=None):
    """
    Saves the results of the fitting to html/rst tables.

    :param software_options : dictionary containing software used in fitting the problem, list of minimizers and location of json file contain minimizers
    :type software_options : dict
    :param minimizers : array with minimizer names
    :type minimizers : list
    :param results_per_test : results nested array of objects
    :type results_per_test : list[list[list]]
    :param group_name : name of the problem group
    :type group_name : str
    :param use_errors : bool whether to use errors or not
    :type use_errors : bool
    :param colour_scale : colour the html table
    :type colour_scale : list
    :param results_dir : name of the problem group
    :type results_dir : str
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

    weighted_str = 'weighted' if use_errors else 'unweighted'

    tables_dir = create_dirs.restables_dir(results_dir, group_name)
    linked_problems = \
        visual_pages.create_linked_probs(results_per_test, group_name, results_dir)

    table_names = []
    for x in [FILENAME_SUFFIX_ACCURACY, FILENAME_SUFFIX_RUNTIME]:
        table_names.append(os.path.join(tables_dir,
                                        '{0}_{1}_{2}_table.'.format(
                                            weighted_str,
                                            x,
                                            group_name)))
    generate_tables(results_per_test, minimizers,
                    linked_problems, color_scale,
                    comparison_mode, table_names)

    logging.shutdown()


def generate_tables(results_per_test, minimizers,
                    linked_problems, colour_scale,
                    comparison_mode, table_names):
    """
    Generates accuracy and runtime tables, with both normalised and absolute results, and summary tables in both rst and html.

    :param results_per_test : results nested array of objects
    :type results_per_test : list[list[list]]
    :param minimizers : array with minimizer names
    :type minimizers : list
    :param linked_problems : rst links for supporting pages
    :type linked_problems : list[str]
    :param colour_scale : colour the html table
    :type colour_scale : list
    :param comparison_mode : check whether to produced 'rel', 'abs' or 'both'
                              tables
    :type comparison_mode : str
    :param table_names : list of table names
    :type table_names : list
    """

    acc_dict, time_dict, html_links = create_results_dict(results_per_test,
                                                          linked_problems)
    acc_tbl = create_pandas_dataframe(acc_dict, minimizers)
    runtime_tbl = create_pandas_dataframe(time_dict, minimizers)

    create_pandas_html(acc_tbl[comparison_mode], runtime_tbl[comparison_mode],
                       minimizers, colour_scale, html_links, table_names)
    create_pandas_rst(acc_tbl[comparison_mode], runtime_tbl[comparison_mode],
                      minimizers, colour_scale, linked_problems, table_names)


def create_results_dict(results_per_test, linked_problems):
    """
    Generates a dictionary used to create HTML and RST tables.

    :param results_per_test : results nested array of objects
    :type results_per_test : list[list[list]]
    :param linked_problems : rst links for supporting pages
    :type linked_problems : list[str]

    :return : tuple(acc_results, time_results, html_links)
               dictionary of accuracy and timing results and
               html links for rending
    :rtype : tuple(dict, dict, list)
    """

    count = 1
    prev_name = ''
    template = '<a target="_blank" href="{0}">{1}</a>'
    acc_results = OrderedDict()
    time_results = OrderedDict()
    html_links = []

    for prob_results, link in zip(results_per_test, linked_problems):
        name = prob_results[0].problem.name
        if name == prev_name:
            count += 1
        else:
            count = 1
        prev_name = name
        prob_name = name + ' ' + str(count)
        url = link.split('<')[1].split('>')[0]
        html_links.append(template.format(url, prob_name))
        acc_results[prob_name] = [result.chi_sq for result in prob_results]
        time_results[prob_name] = [result.runtime for result in prob_results]
    return acc_results, time_results, html_links


def create_pandas_dataframe(table_data, minimizers):
    """
    Generates pandas tables.

    :param table_data : dictionary containing results, i.e.,
                            {'prob1': [result1, result2, ...],
                             'prob2': [result1, result2, ...], ...}
    :type table_data : dict
    :param minimizers : list of minimizers (column headers)
    :type group_name : list


    :return : dict(tbl, tbl_norm, tbl_combined) dictionary of
               pandas DataFrames containing results.
    :rtype : dict{pandas DataFrame, pandas DataFrame,
                   pandas DataFrame}
    """

    tbl = pd.DataFrame.from_dict(table_data, orient='index')
    tbl.columns = minimizers

    tbl_norm = tbl.apply(lambda x: x / x.min(), axis=1)
    tbl_norm = tbl_norm.applymap(lambda x: '{:.4g}'.format(x))
    tbl = tbl.applymap(lambda x: '{:.4g}'.format(x))

    tbl_combined = OrderedDict()
    for table1, table2 in zip(tbl.iterrows(), tbl_norm.iterrows()):
        tbl_combined[table1[0]] = []
        for value1, value2 in zip(table1[1].array, table2[1].array):
            tbl_combined[table1[0]].append('{} ({})'.format(value1, value2))
    tbl_combined = pd.DataFrame.from_dict(tbl_combined, orient='index')
    tbl_combined.columns = minimizers
    results_table = {'abs': tbl, 'rel': tbl_norm, 'both': tbl_combined}
    return results_table


def check_normalised(data, colours, colour_bounds):
    """
    Loops through row data of pandas data frame and assigns
    colours depending on size.

    :param data : Pandas row data
    :type data : Pandas Series
    :param colours : rst or html colour definitions
    :type colours : list[str]
    :param colour_bounds : rst or html colour bounds
    :type colour_bounds : list[str]

    :return : list of colour mappings with respect to the
               size of the elements in the row
    :rtype : list
    """

    data_numpy = data.array.to_numpy()
    data_list = []
    for x in data_numpy:
        x = x.replace('nan', 'inf')
        norm_stripped = re.findall('\(([^)]+)', x)
        if norm_stripped == []:
            data_list.append(float(x))
        else:
            data_list.append(float(norm_stripped[0]))

    data_list = data_list / np.min(data_list)
    results = len(data_list) * [colours[-1]]
    for i, x in enumerate(data_list):
        for j, y in enumerate(colour_bounds):
            if x <= y:
                results[i] = colours[j]
                break
    return results


def create_pandas_html(acc_tbl, runtime_tbl, minimizers,
                       colour_scale, html_links, table_names):
    """
    Generates html page from pandas dataframes.

    :param acc_tbl : DataFrame of the accuracy results
    :type acc_tbl : pandas DataFrame
    :param runtime_tbl : DataFrame of the timing results
    :type runtime_tbl : pandas DataFrame
    :param minimizers : list of minimizers (column headers)
    :type minimizers : list
    :param colour_scale : user defined colour scale
    :type colour_scale : list
    :param html_links : html links used in pandas rendering
    :type html_links : list
    :param table_names : list of table names
    :type table_names : list
    """
    colour_bounds = [colour[0] for colour in colour_scale]

    acc_tbl.index = html_links
    runtime_tbl.index = html_links

    def colour_highlight(data):
        '''
        Colour mapping for visualisation of table
        '''
        data_list = check_normalised(data, HTML_COLUR_SCALE, colour_bounds)

        return ['background-color: {0}'.format(i) for i in data_list]
    results = [acc_tbl, runtime_tbl]
    for table, name in zip(results, table_names):
        table_style = table.style.apply(colour_highlight, axis=1)
        with open(name + 'html', "w") as f:
            f.write(table_style.render())


def create_pandas_rst(acc_tbl, runtime_tbl, minimizers,
                      colour_scale, rst_links, table_names):
    """
    Generates html page from pandas dataframes.

    :param acc_tbl : DataFrame of the accuracy results
    :type acc_tbl : pandas DataFrame
    :param runtime_tbl : DataFrame of the timing results
    :type runtime_tbl : pandas DataFrame
    :param minimizers : list of minimizers (column headers)
    :type minimizers : list
    :param colour_scale : user defined colour scale
    :type colour_scale : list
    :param rst_links : rst links used in pandas rendering
    :type rst_links : list
    :param table_names : list of table names
    :type table_names : list
    """
    colour_bounds = [colour[0] for colour in colour_scale]
    rst_colours = [colour[1] for colour in colour_scale]

    acc_tbl.index = rst_links
    runtime_tbl.index = rst_links

    def colour_highlight(data):
        '''
        Colour mapping for visualisation of table
        '''
        data_list = check_normalised(data, rst_colours, colour_bounds)
        for i, x in enumerate(data):
            data[i] = ':{}:`{}`'.format(data_list[i], x)

        return data

    results = [acc_tbl, runtime_tbl]
    for table, name in zip(results, table_names):
        table.apply(colour_highlight, axis=1)
        writer = pytablewriter.RstGridTableWriter()
        writer.from_dataframe(table, add_index_column=True)
        writer.dump(name + "rst")
