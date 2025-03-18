"""
Runtime table
"""

from fitbenchmarking.results_processing.base_table import Table


class RuntimeTable(Table):
    """

    The timing results are calculated from an average (over num_runs) using the
    `timeit <https://docs.python.org/2/library/timeit.html>`_  module
    in python. num_runs is set in :ref:`options`.

    """

    name = "runtime"
    cbar_title = "Problem-Specific Cell Shading: Relative Runtime"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative runtime) will be used in the
        default colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised runtime with respect to the smallest runtime
                 and absolute runtime for the result.
        :rtype: tuple(float, float)
        """
        rel_value = result.norm_runtime()
        abs_value = result.runtime
        return rel_value, abs_value

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
        val_str = (
            f"<a {self.color_to_class[text_col]} "
            f'href="{self.get_link_str(result)}">'
            f"{self.get_runtime_value_str(result, val_str)}</a>"
        )
        return val_str
