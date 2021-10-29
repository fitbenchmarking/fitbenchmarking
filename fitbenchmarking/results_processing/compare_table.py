"""
compare table
"""
import os

from fitbenchmarking.results_processing.base_table import Table


class CompareTable(Table):
    """

    The combined results show the accuracy in the first line of the cell and
    the runtime on the second line of the cell.

    """

    def __init__(self, results, best_results, options, group_dir, pp_locations,
                 table_name):
        """
        Initialise the compare table which shows both accuracy and runtime
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
        self.name = 'compare'
        self.has_pp = True
        self.pp_filenames = \
            [os.path.relpath(pp, group_dir) for pp in pp_locations]

        self.colour_template = \
            'background-image: linear-gradient({0},{0},{1},{1})'

        self.cbar_title = "Problem-Specific Cell Shading:\n"\
                          "Top Colour - Relative Accuracy\n"\
                          "Bottom Colour - Relative Runtime\n"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative chi_sq) will be used in the default
        colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised chi sq and runtime with respect to the smallest
                 chi_sq and runtime respectively as well as the absolute values
                 for both chi_sq and runtime for the result.
                 [[acc_rel, runtime_rel], [acc_abs, runtime_abs]]
        :rtype: list[list[float]]
        """
        acc_rel = result.norm_acc
        acc_abs = result.chi_sq

        runtime_rel = result.norm_runtime
        runtime_abs = result.runtime

        return [[acc_rel, runtime_rel],
                [acc_abs, runtime_abs]]

    def display_str(self, value):
        """
        Combine the accuracy and runtime values into a string representation.

        :param value: Relative and absolute values for accuracy and runtime
                      [[acc_rel, runtime_rel], [acc_abs, runtime_abs]]
        :type value: list[list[float]]

        :return: string representation of the value for display in the table.
        :rtype: str
        """
        (acc_rel, runtime_rel), (acc_abs, runtime_abs) = value
        comp_mode = self.options.comparison_mode
        result_template = self.output_string_type[self.options.comparison_mode]

        if comp_mode == "abs":
            return result_template.format(acc_abs) + '<br>' + \
                result_template.format(runtime_abs)
        if comp_mode == "rel":
            return result_template.format(acc_rel) + '<br>' + \
                result_template.format(runtime_rel)
        # comp_mode == "both":
        return result_template.format(acc_abs, acc_rel) + '<br>' + \
            result_template.format(runtime_abs, runtime_rel)

    def vals_to_colour(self, vals, *args):
        """
        Override vals_to_colour to allow it to run for both accuracy and
        runtime.

        :param vals: The relative values to get the colours for
        :type vals: list[list[float, float]]

        :return: The colours for the values
        :rtype: list[list[str]]
        """
        acc, runtime = zip(*vals)
        acc_colours = super().vals_to_colour(acc, *args)
        runtime_colours = super().vals_to_colour(runtime, *args)
        return zip(acc_colours, runtime_colours)
