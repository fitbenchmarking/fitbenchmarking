"""
compare table
"""

from fitbenchmarking.results_processing.base_table import Table


class CompareTable(Table):
    """

    The combined results show the accuracy in the first line of the cell and
    the runtime on the second line of the cell.

    For Bayesian fitting, accuracy results represent the reciporcal of the
    confidence that the fitted parameter values are within :math:`2 \\sigma`
    of the expected parameter values (calculated using
    scipy.optimize.curve_fit).

    """

    name = "compare"
    colour_template = "background-image: linear-gradient({0},{0},{1},{1})"
    cbar_title = (
        "Problem-Specific Cell Shading:\n"
        "Top Colour - Relative Accuracy\n"
        "Bottom Colour - Relative Runtime\n"
    )

    def __init__(
        self,
        results,
        best_results,
        options,
        group_dir,
        pp_locations,
        table_name,
    ):
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
        :param pp_locations: the locations of the performance profiles
        :type pp_locations: dict[str,str]
        :param table_name: Name of the table
        :type table_name: str
        """
        super().__init__(
            results, best_results, options, group_dir, pp_locations, table_name
        )
        self.pps = ["acc", "runtime"]

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
        acc_abs = result.accuracy

        runtime_rel = result.norm_runtime
        runtime_abs = result.runtime

        return [[acc_rel, runtime_rel], [acc_abs, runtime_abs]]

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
            return (
                result_template.format(acc_abs)
                + "<br>"
                + result_template.format(runtime_abs)
            )
        if comp_mode == "rel":
            return (
                result_template.format(acc_rel)
                + "<br>"
                + result_template.format(runtime_rel)
            )
        # comp_mode == "both":
        return (
            result_template.format(acc_abs, acc_rel)
            + "<br>"
            + result_template.format(runtime_abs, runtime_rel)
        )

    @staticmethod
    def vals_to_colour(vals, cmap, cmap_range, log_ulim):
        """
        Override vals_to_colour to allow it to run for both accuracy and
        runtime.

        :param vals: The relative values to get the colours for
        :type vals: list[list[float, float]]
        :param cmap: matplotlib colourmap
        :type cmap: matplotlib colourmap object
        :param cmap_range: values in range [0, 1] for colourmap cropping
        :type cmap_range: list[float], 2 elements
        :param log_ulim: log10 of worst shading cutoff value
        :type log_ulim: float

        :return: The background colours for the acc and runtime values and
                 The text colours for the acc and runtime values
        :rtype: tuple[zip[list[str], list[str]], zip[list[str], list[str]]]
        """
        acc, runtime = zip(*vals)
        acc_colours, acc_text = Table.vals_to_colour(
            acc, cmap, cmap_range, log_ulim
        )
        runtime_colours, runtime_text = Table.vals_to_colour(
            runtime, cmap, cmap_range, log_ulim
        )
        background_col = zip(acc_colours, runtime_colours)
        foreground_text = zip(acc_text, runtime_text)
        return background_col, foreground_text

    def get_hyperlink(self, result, val_str, text_col):
        """
        Generates the hyperlink for a given result

        :param result: The result to generate a string for
        :type result: fitbenchmarking.utils.ftibm_result.FittingResult
        :param val_str: Preprocessed val_str to display
        :type val_str: str
        :param text_col: Foreground colour for the text as html rgb strings
                         e.g. 'rgb(255, 255, 255)'
        :type text_col: str

        :return: The hyperlink representation.
        :rtype: str
        """
        color_to_class = {
            "rgb(0,0,0)": 'class="dark"',
            "rgb(255,255,255)": 'class="light"',
        }
        ftext, stext = text_col
        val_str = val_str.split("<br>")
        val_str = (
            f"<a {color_to_class[ftext]} "
            f'href="{self.get_link_str(result)}">'
            f"{val_str[0]}</a>"
            f"<a {color_to_class[stext]} "
            f'href="{self.get_link_str(result)}">'
            f"{val_str[1]}</a>"
        )
        return val_str
