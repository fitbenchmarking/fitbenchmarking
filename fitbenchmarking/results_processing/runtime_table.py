"""
Runtime table
"""
import numpy as np
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
        Initialise runtime table class.

        :param results: dictionary containing results, i.e.,
                           {'prob1': [result1, result2, ...],
                            'prob2': [result1, result2, ...], ...}
        :type results: dict
        :param options: The options used in the fitting problem and plotting
        :type options: fitbenchmarking.utils.options.Options
        """
        self.name = 'runtime'
        super(RuntimeTable, self).__init__(results, best_results, options,
                                           group_dir, pp_locations, table_name)

        self.has_pp = True
        self.pp_filenames = [self.pp_locations[1]]

    def get_values(self, results_dict):
        abs_value = {}
        rel_value = {}
        for key, value in results_dict.items():
            abs_value[key] = [v.runtime for v in value]
            min_value = np.min(abs_value[key])
            rel_value[key] = [v.runtime / min_value for v in value]

        return abs_value, rel_value
