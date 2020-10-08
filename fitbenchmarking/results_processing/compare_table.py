"""
compare table
"""
import numpy as np
import os
from fitbenchmarking.results_processing.base_table import Table


class CompareTable(Table):
    """

    The combined results show the accuracy in the first line of the cell and
    the runtime on the second line of the cell.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations, table_name):
        """
        Initialise the compare table which shows both accuracy and runtime
        results

        :param results: results nested array of objects
        :type results: list of list of
                       fitbenchmarking.utils.fitbm_result.FittingResult
        :param best_results: best result for each problem
        :type best_results: list of
                        fitbenchmarking.utils.fitbm_result.FittingResult
        :param options: Options used in fitting
        :type options: utils.options.Options
        :param group_dir: path to the directory where group results should be
                          stored
        :type group_dir: str
        :param pp_locations: tuple containing the locations of the
                             performance profiles (acc then runtime)
        :type pp_locations: tuple(str,str)
        :param table_name: Name of the table
        :type table_name: str
        """
        self.name = 'compare'
        super(CompareTable, self).__init__(results, best_results, options,
                                           group_dir, pp_locations, table_name)

        self.has_pp = True
        self.pp_filenames = \
                        [os.path.relpath(pp,group_dir) for pp in pp_locations]

    def get_values(self, results_dict):
        """
        Gets the main values to be reported in the tables

        :param results_dict: dictionary containing results where the keys
                             are the problem sets and the values are lists
                             of results objects
        :type results_dict: dictionary

        :return: First dictionary containing the absolute chi_sq and runtime
                 results and the second contains the normalised chi_sq and
                 runtime results with respect to the smallest values.
        :rtype: tuple(dict, dict)
        """
        abs_value = {}
        rel_value = {}
        for key, value in results_dict.items():
            acc_abs_value = [v.chi_sq for v in value]
            acc_min_value = np.min(acc_abs_value)
            acc_rel_value = [v.chi_sq / acc_min_value for v in value]

            runtime_abs_value = [v.runtime for v in value]
            runtime_min_value = np.min(runtime_abs_value)
            runtime_rel_value = [v.runtime / runtime_min_value for v in value]

            abs_value[key] = [acc_abs_value, runtime_abs_value]
            rel_value[key] = [acc_rel_value, runtime_rel_value]

        return abs_value, rel_value

    def display_str(self, results):
        """
        Function that combines the accuracy and runtime results into the
        string representation.

        :param results: tuple containing absolute and relative values
        :type results: tuple

        :return: dictionary containing the string representation of the values
                 in the table.
        :rtype: dict
        """
        abs_results, rel_results = results
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[self.options.comparison_mode]
        table_output = {}
        for key in abs_results.keys():
            acc_abs, runtime_abs = abs_results[key]
            acc_rel, runtime_rel = rel_results[key]
            if comp_mode == "abs":
                table_output[key] = \
                    [result_template.format(acc) + '<br>'
                     + result_template.format(runtime)
                     for acc, runtime in zip(acc_abs, runtime_abs)]
            elif comp_mode == "rel":
                table_output[key] = \
                    [result_template.format(acc) + '<br>'
                     + result_template.format(runtime)
                     for acc, runtime in zip(acc_rel, runtime_rel)]
            elif comp_mode == "both":
                table_output[key] = \
                    [result_template.format(acc_a, acc_r) + '<br>'
                     + result_template.format(runtime_a, runtime_r)
                     for acc_a, acc_r, runtime_a, runtime_r in
                     zip(acc_abs, acc_rel, runtime_abs, runtime_rel)]
        return table_output

    def colour_highlight(self, value, colour):
        """
        Enable HTML colours in the HTML output.

        :param value: Row data from the pandas array
        :type value: pandas.core.series.Series
        :param colour: dictionary containing error codes from the minimizers
        :type colour: dict

        :return: list of HTML colours
        :rtype: list
        """
        color_template = 'background-image: linear-gradient({0},{0},{1},{1})'
        name = value.name.split('"')[2].replace("</a>", "")[1:]
        output_colour = []
        acc_colour, runtime_colour = colour[name]
        for acc, runtime in zip(acc_colour, runtime_colour):
            output_colour.append(color_template.format(acc, runtime))
        return output_colour
