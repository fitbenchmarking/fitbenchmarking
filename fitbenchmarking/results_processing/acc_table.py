"""
Accuracy table
"""
import os

from fitbenchmarking.results_processing.base_table import Table


class AccTable(Table):
    """

    The accuracy results are calculated by evaluating the cost function with
    the fitted parameters.

    For Bayesian fitting, accuracy results represent the reciporcal of the
    confidence that the fitted parameter values are within :math:`2 \\sigma`
    of the expected parameter values (calculated using
    scipy.optimize.curve_fit).

    """

    def __init__(self, results, best_results, options, group_dir, pp_locations,
                 table_name):
        """
        Initialise the accuracy table which shows the acc results

        :param results: Results grouped by row and category (for colouring)
        :type results:
            dict[str, dict[str, list[utils.fitbm_result.FittingResult]]]
        :param best_results: The best results from each row/category
        :type best_results:
            dict[str, dict[str, utils.fitbm_result.FittingResult]],
        :param options: Options used in fitting
        :type options: utils.options.Options
        :param group_dir: path to the directory where group results should be
                          stored
        :type group_dir: str
        :param pp_locations: the locations of the performance profiles
        :type pp_locations: dict[str,str]
        :param table_name: Name of the table
        :type table_name: str
        """
        super().__init__(results, best_results, options, group_dir,
                         pp_locations, table_name)
        self.name = 'acc'
        self.has_pp = True
        port = options.port
        group_dir_label = os.path.basename(group_dir)

        self.pp_dash_urls = [f'http://127.0.0.1:{port}/{group_dir_label}/'
                             'perf_prof_acc']
        self.pp_filenames = [
            os.path.relpath(self.pp_locations['acc'], group_dir)
        ]
        self.cbar_title = "Problem-Specific Cell Shading: Relative Accuracy"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative accuracy) will be used in the
        default colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised chi sq with respect to the smallest accuracy
                 value and absolute accuracy for the result.
        :rtype: tuple(float, float)
        """
        rel_value = result.norm_acc
        abs_value = result.accuracy
        return rel_value, abs_value
