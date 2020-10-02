"""
Runtime table
"""
import numpy as np
import os
from fitbenchmarking.results_processing.base_table import Table


class RuntimeTable(Table):
    """

    The timing results are calculated from an average using the
    `timeit <https://docs.python.org/2/library/timeit.html>`_  module
    in python. The number of runtimes can be set in :ref:`options`.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations, table_name):
        """
        Initialise the runtime table which shows the average runtime results

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

        self.name = 'runtime'
        super(RuntimeTable, self).__init__(results, best_results, options,
                                           group_dir, pp_locations, table_name)

        self.has_pp = True
        self.pp_filenames = [os.path.relpath(self.pp_locations[1],group_dir)]

    def get_values(self, results_dict):
        """
        Gets the main values to be reported in the tables

        :param results_dict: dictionary containing results where the keys
                             are the problem sets and the values are lists
                             of results objects
        :type results_dict: dictionary

        :return: two dictionaries containing the absolute runtime and the
                 normalised runtime with respect to the quickest time.
        :rtype: tuple(dict, dict)
        """
        abs_value = {}
        rel_value = {}
        for key, value in results_dict.items():
            abs_value[key] = [v.runtime for v in value]
            min_value = np.min(abs_value[key])
            rel_value[key] = [v.runtime / min_value for v in value]

        return abs_value, rel_value
