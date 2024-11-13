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
        rel_value = result.norm_runtime
        abs_value = result.runtime
        return rel_value, abs_value
