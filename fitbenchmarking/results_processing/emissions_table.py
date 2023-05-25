"""
Emissions table
"""
import os

from fitbenchmarking.results_processing.base_table import Table


class EmissionsTable(Table):
    r"""

    The emissions (kg CO\ :sub:`2`\ eq) results are calculated
    from an average (over num_runs) using the
    `codecarbon <https://mlco2.github.io/codecarbon/index.html>`_  module.
    num_runs is set in :ref:`options`.

    Configuration for codecarbon is set in ``.codecarbon.config``.

    """

    def __init__(self, results, best_results, options, group_dir, pp_locations,
                 table_name):
        """
        Initialise the emissions table which shows the average emissions
        results

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
        self.name = 'emissions'
        self.has_pp = True
        self.pp_filenames = [os.path.relpath(self.pp_locations[1], group_dir)]

        self.cbar_title = "Problem-Specific Cell Shading: Relative Emissions"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative emissions) will be used in the
        default colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised emissions with respect to the smallest
                 emissions value and absolute emissions for the result.
        :rtype: tuple(float, float)
        """
        rel_value = result.norm_emissions
        abs_value = result.emissions
        return rel_value, abs_value
