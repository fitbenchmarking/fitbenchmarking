"""
Accuracy table
"""
from fitbenchmarking.results_processing.base_table import Table


class AccTable(Table):
    """

    The accuracy results are calculated by evaluating the cost function with
    the fitted parameters.

    For Bayesian fitting, accuracy results represent the confidence that the
    fitted parameter values are within 10% of the expected parameter values
    (calculated using scipy.optimize.minimize).

    """
    name = 'acc'
    cbar_title = "Problem-Specific Cell Shading: Relative Accuracy"

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
