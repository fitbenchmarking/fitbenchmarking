"""
Functions that creates the tables and the visual display pages.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
import logging
import os
import pandas as pd
import numpy as np
import re


from fitbenchmarking.utils.logging_setup import logger
from fitbenchmarking.resproc import visual_pages
from fitbenchmarking.utils import create_dirs, options, misc

# Some naming conventions for the output files
FILENAME_SUFFIX_ACCURACY = 'acc'
FILENAME_SUFFIX_RUNTIME = 'runtime'
FILENAME_EXT_TXT = 'txt'
FILENAME_EXT_HTML = 'html'

html_color_scale = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']


def save_results_tables(software_options, results_per_test, group_name,
                        use_errors, color_scale=None, results_dir=None):
    """
    Saves the results of the fitting to html/rst tables.

    @param software_options :: dictionary containing software used in fitting the problem, list of minimizers and location of json file contain minimizers
    @param minimizers :: array with minimizer names
    @param results_per_test :: results nested array of objects
    @param group_name :: name of the problem group
    @param use_errors :: bool whether to use errors or not
    @param colour_scale :: colour the html table
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

    generate_tables(results_per_test, minimizers, linked_problems, color_scale)

    logging.shutdown()


def generate_tables(results_per_test, minimizers,
                    linked_problems, colour_scale):
    """
    Generates accuracy and runtime tables, with both normalised and absolute results, and summary tables.

    @param results_per_test :: results nested array of objects
    @param minimizers :: array with minimizer names
    linked_problems ::

    @returns :: data and summary tables of the results as np arrays
    """

    acc_dict, time_dict = create_results_dict(results_per_test,
                                              linked_problems)

    create_pandas_rst(acc_dict[FILENAME_EXT_TXT],
                      time_dict[FILENAME_EXT_TXT],
                      minimizers, colour_scale)
    create_pandas_html(acc_dict[FILENAME_EXT_HTML],
                       time_dict[FILENAME_EXT_HTML],
                       minimizers, colour_scale)


def create_results_dict(results_per_test, linked_problems):
    """
    Generates a dictionary used to create HTML and RST tables.

    @param results_per_test :: results nested array of objects
    linked_problems ::

    @returns :: data and summary tables of the results as np arrays
    """

    count = 1
    prev_name = ''
    table_name = OrderedDict()
    template = '<a target="_blank" href="{0}">{1}</a>'
    acc_results = OrderedDict()
    time_results = OrderedDict()
    acc_results[FILENAME_EXT_HTML] = OrderedDict()
    acc_results[FILENAME_EXT_TXT] = OrderedDict()
    time_results[FILENAME_EXT_HTML] = OrderedDict()
    time_results[FILENAME_EXT_TXT] = OrderedDict()
    for test_idx, prob_results in enumerate(results_per_test):
        name = results_per_test[test_idx][0].problem.name
        if name == prev_name:
            count += 1
        else:
            count = 1
        prev_name = name
        prob_name = name + ' ' + str(count)
        name, url = linked_problems[test_idx].split('<')
        table_name[FILENAME_EXT_HTML] = \
            template.format(url.split('>')[0], prob_name)
        table_name[FILENAME_EXT_TXT] = linked_problems[test_idx]

        for key, value in table_name.items():
            acc_results[key][value] = [result.chi_sq for result in results_per_test[test_idx]]
            time_results[key][value] = [result.runtime for result in results_per_test[test_idx]]

    return acc_results, time_results


def create_pandas_html(acc_dict, time_dict, minimizers, colour_scale):
    """
    Generates a pandas data frame used to create the html tables.

    @param results_per_test :: results nested array of objects
    @param minimizers :: array with minimizer names
    linked_problems ::

    @returns :: data and summary tables of the results as np arrays
    """
    acc_tbl = \
        create_tables(acc_dict, minimizers)
    runtime_tbl = \
        create_tables(time_dict, minimizers)

    def highlight_max(data, color='yellow'):
        '''
        highlight the maximum in a Series or DataFrame
        '''
        data_numpy = data.array.to_numpy()
        data = []
        for x in data_numpy:
            norm_stripped = re.findall('\(([^)]+)', x)
            if norm_stripped == []:
                data.append(float(x))
            else:
                data.append(float(norm_stripped[0]))
        data = data / np.min(data)
        data = np.select(
            [data <= 1.1, data <= 1.33, data <= 1.75, data <= 3, data > 3],
            html_color_scale)

        return ['background-color: {0}'.format(i) for i in data]

    for i, table in enumerate(acc_tbl + runtime_tbl):
        acc_style = table.style.apply(highlight_max, axis=1)

        f = open("test{0}.html".format(i), "w")
        f.write(acc_style.render())  # df is the styled dataframe
        f.close()
    return 1


def create_pandas_rst(acc_dict, time_dict, minimizers, colour_scale):
    """
    Generates a pandas data frame used to create the rst tables.

    @param results_per_test :: results nested array of objects
    @param minimizers :: array with minimizer names
    linked_problems ::
    colour_scale ::

    @returns :: data and summary tables of the results as np arrays
    """
    import pytablewriter

    acc_tbl = create_tables_rst(acc_dict, minimizers, colour_scale)
    runtime_tbl = create_tables_rst(time_dict, minimizers, colour_scale)
    for table in acc_tbl + runtime_tbl:
        writer = pytablewriter.RstGridTableWriter()
        writer.table_name = "example_table"
        writer.from_dataframe(table, add_index_column=True)
        # table = writer.write_table()

    return 1


def create_tables_rst(table_data, minimizers, colour_scale):
    """
    Generates pandas dataframes in rst format.

    :param table_data :: dictionary containing results
    :type group_name :: dict
    :param minimizers :: list of minimizers (column headers)
    :type minimizers :: list
    :param colour_scale :: user defined colour scale
    :type colour_scale :: list


    :return :: list(tbl, tbl_norm, tbl_combined) array of fitting results for
                the problem group and the path to the results directory
    :rtype :: [pandas DataFrame, pandas DataFrame, pandas DataFrame]
    """
    normalised_table_dict = OrderedDict()
    combined_table_dict = OrderedDict()

    colour_template = ':{}:`{:.4e}`'
    colour_combined_template = ':{}:`{:.4e} ({:.4e})`'

    template = '{:.4e}'
    combined_template = '{:.4e} ({:.4e})`'
    for key, value in table_data.items():
        normalised = (value / np.min(value))
        colour_format = len(normalised) * ['']
        if isinstance(colour_scale, list):
            for i, x in enumerate(normalised):
                start = 1.0
                colour_format[i] = 'ranking-low-5'
                for colour in colour_scale:
                    end = colour[0]

                    if start <= float(x) <= end:
                        colour_format[i] = colour[1]

                    start = end

            table_data[key] = [colour_template.format(colour, data) for colour, data in zip(colour_format, value)]

            normalised_table_dict[key] = [colour_template.format(colour, data) for colour, data in zip(colour_format, normalised)]

            combined_table_dict[key] = []
            for colour, value1, value2 in zip(colour_format,
                                              value, normalised):
                combined_table_dict[key].append(colour_combined_template.format(
                    colour,
                    value1,
                    value2))
        else:

            table_data[key] = [template.format(data) for data in value]

            normalised_table_dict[key] = [template.format(data) for data in normalised]

            combined_table_dict[key] = [combined_template.format(v1, v2)
                                        for v1, v2 in zip(value, normalised)]

    tbl = pd.DataFrame.from_dict(table_data, orient='index')
    tbl.columns = minimizers

    tbl_norm = pd.DataFrame.from_dict(normalised_table_dict, orient='index')
    tbl_norm.columns = minimizers

    tbl_combined = pd.DataFrame.from_dict(combined_table_dict, orient='index')
    tbl_combined.columns = minimizers

    return [tbl, tbl_norm, tbl_combined]


def create_tables(table_data, minimizers):
    """
    Generates pandas tables.

    :param table_data :: dictionary containing results
    :type group_name :: dict
    :param minimizers :: list of minimizers (column headers)
    :type group_name :: list


    :return :: list(tbl, tbl_norm, tbl_combined) array of fitting results for
                the problem group and the path to the results directory
    :rtype :: [pandas DataFrame, pandas DataFrame, pandas DataFrame]
    """

    tbl = pd.DataFrame.from_dict(table_data, orient='index')
    tbl.columns = minimizers

    tbl_norm = tbl.apply(lambda x: x / x.min(), axis=1)
    tbl_norm = tbl_norm.applymap(lambda x: '{:.4e}'.format(x))
    tbl = tbl.applymap(lambda x: '{:.4e}'.format(x))

    tbl_combined = OrderedDict()
    for table1, table2 in zip(tbl.iterrows(), tbl_norm.iterrows()):
        tbl_combined[table1[0]] = []
        for value1, value2 in zip(table1[1].array, table2[1].array):
            tbl_combined[table1[0]].append('{} ({})'.format(value1, value2))
    tbl_combined = pd.DataFrame.from_dict(tbl_combined, orient='index')
    tbl_combined.columns = minimizers

    return [tbl, tbl_norm, tbl_combined]
