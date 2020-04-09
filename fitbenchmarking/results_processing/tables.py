"""
Set up and build the results tables.
"""

from __future__ import (absolute_import, division, print_function)
from collections import OrderedDict
from importlib import import_module
from inspect import getfile, getmembers, isabstract, isclass
from jinja2 import Environment, FileSystemLoader
import os

import fitbenchmarking
from fitbenchmarking.results_processing.base_table import Table

ERROR_OPTIONS = {0: "Successfully converged",
                 1: "Software reported maximum number of iterations exceeded",
                 2: "Software run but didn't converge to solution",
                 3: "Software raised an exception"}

SORTED_TABLE_NAMES = ["compare", "acc", "runtime", "local_min"]
# SORTED_TABLE_NAMES = ["local_min"]


def create_results_tables(options, results, best_results, group_name,
                          group_dir, pp_locations):
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


    :return: filepaths to each table
             e.g {'acc': <acc-table-filename>, 'runtime': ...}
    :rtype: dict
    """

    weighted_str = 'weighted' if options.use_errors else 'unweighted'

    table_names = {}
    description = {}
    for suffix in SORTED_TABLE_NAMES:
        if suffix in options.table_type:
            table_names[suffix] = '{0}_{1}_{2}_table.'.format(group_name,
                                                              suffix,
                                                              weighted_str)

            table = create_table(suffix)
            table = table(results, best_results,
                          options, group_dir,
                          pp_locations)
            table.create_data_frame()
            acc_html = table.to_html()

            table_title = table.table_title
            file_path = os.path.join(group_dir, table_names[suffix])
            description = table.get_description(description)

            table_format = None if suffix == 'local_min' \
                else description[options.comparison_mode]

            has_pp = table.has_pp
            pp_filenames = table.pp_filenames

            root = os.path.dirname(getfile(fitbenchmarking))
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
                                        table_description=description[suffix],
                                        table_format=table_format,
                                        result_name=table_title,
                                        has_pp=has_pp,
                                        pp_filenames=pp_filenames,
                                        table=acc_html,
                                        error_message=ERROR_OPTIONS))

    return table_names, description


def create_table(table):
    """
    Create a controller that matches the required software.

    :param software: The name of the software to create a controller for
    :type software: string

    :return: Controller class for the problem
    :rtype: fitbenchmarking.fitting.base_controller.Controller subclass
    """

    module_name = '{}_table'.format(table.lower())

    try:
        module = import_module('.' + module_name, __package__)
    except ImportError as e:
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                 module_name + '.py'))
        if os.path.exists(full_path):
            raise MissingSoftwareError('Requirements are missing for the '
                                       '{} controller: {}'.format(
                                           software, e))
        else:
            raise NoControllerError('Could not find controller for {}. '
                                    'Check the input is correct and try '
                                    'again.'.format(software))
    classes = getmembers(module, lambda m: (isclass(m)
                                            and not isabstract(m)
                                            and issubclass(m, Table)
                                            and m is not Table))
    return classes[0][1]
