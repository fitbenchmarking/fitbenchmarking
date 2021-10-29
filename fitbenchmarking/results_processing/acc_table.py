"""
Accuracy table
"""
import os

from fitbenchmarking.results_processing.base_table import Table


class AccTable(Table):
    """

    The accuracy results are calculated by evaluating the cost function with
    the fitted parameters.

    """

    def __init__(self, results, best_results, options, group_dir, pp_locations,
                 table_name):
        """
        Initialise the accuracy table which shows the chi_sq results

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
        :param pp_locations: tuple containing the locations of the
                             performance profiles (acc then runtime)
        :type pp_locations: tuple(str,str)
        :param table_name: Name of the table
        :type table_name: str
        """
        super().__init__(results, best_results, options, group_dir,
                         pp_locations, table_name)
        self.name = 'acc'
        self.has_pp = True
        self.pp_filenames = [os.path.relpath(self.pp_locations[0], group_dir)]

        self.cbar_title = "Problem-Specific Cell Shading: Relative Accuracy"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative chi_sq) will be used in the default
        colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised chi sq with respect to the smallest chi_sq
                 value and absolute chi_sq for the result.
        :rtype: tuple(float, float)
        """
        rel_value = result.norm_acc
        abs_value = result.chi_sq
        return rel_value, abs_value
