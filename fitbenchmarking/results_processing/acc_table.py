"""
Accuracy table
"""
import os
import numpy as np
from fitbenchmarking.results_processing.base_table import Table


class AccTable(Table):
    """

    The accuracy results are calculated by evaluating the cost function with
    the fitted parameters.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations, table_name):
        """
        Initialise the accuracy table which shows the chi_sq results

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
        super().__init__(results, best_results, options,
                         group_dir, pp_locations, table_name)
        self.name = 'acc'
        self.has_pp = True
        self.pp_filenames = [os.path.relpath(self.pp_locations[0], group_dir)]

    def get_values(self, results_dict):
        """
        Gets the main values to be reported in the tables

        :param results_dict: dictionary containing results where the keys
                             are the problem sets and the values are lists
                             of results objects
        :type results_dict: dictionary

        :return: two dictionaries containing the absolute chi_sq and the
                 normalised chi_sq with respect to the smallest chi_sq value.
        :rtype: tuple(dict, dict)
        """
        abs_value = {}
        rel_value = {}
        for key, value in results_dict.items():
            abs_value[key] = [v.chi_sq for v in value]

            # exclude results with error flag 5
            error_flags = [v.error_flag for v in value]
            to_exclude = [i for i, e in enumerate(error_flags) if e == 5]

            min_value = np.min(abs_value[key])
            rel_value[key] = [v.chi_sq / min_value for v in value]

            min_value = np.min([x for i, x in enumerate(
                abs_value[key]) if i not in to_exclude])
            rel_value[key] = [v.chi_sq / min_value if v.error_flag !=
                              5 else np.inf for v in value]

        return abs_value, rel_value


    def get_cbar(self, fig_dir):
        """
        Plots colourbar figure to figure directory and returns the 
        path to the figure.

        :param fig_dir: figure directory
        :type fig_dir: str

        :return fig_path: path to colourbar figure
        :rtype fig_path: str
        """
        cmap_name = self.options.colour_map
        cmap_range = self.options.cmap_range
        colour_ulim = self.options.colour_ulim
        fig_path = os.path.join(fig_dir, "{0}_cbar.png".format(self.name))
        title = "Problem-Specific Cell Shading: Relative Accuracy"
        left_label = "Best (1)"
        right_label = "Worst (>{})".format(colour_ulim)


        self._save_colourbar(fig_path, cmap_name, cmap_range, title, left_label,
                        right_label)
        
        return fig_path