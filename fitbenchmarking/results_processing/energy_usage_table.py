"""
Energy Usage table
"""

from fitbenchmarking.results_processing.base_table import Table


class EnergyUsageTable(Table):
    r"""

    The energy usage (kWh) results are calculated
    from an average (over num_runs) using the
    `codecarbon <https://mlco2.github.io/codecarbon/index.html>`_  module.
    num_runs is set in :ref:`options`.

    Configuration for codecarbon is set in ``.codecarbon.config``.

    For more information on how energy usage is measured,
    see the Methodology section of the `codecarbon docs
    <https://mlco2.github.io/codecarbon/methodology.html#cpu>`_.

    """

    name = "energy_usage"
    cbar_title = "Problem-Specific Cell Shading: Relative Energy Usage"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative energy usage) will be used in the
        default colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: The normalised energy usage with respect to the smallest
                 energy value and absolute energy for the result.
        :rtype: tuple(float, float)
        """
        rel_value = result.norm_energy
        abs_value = result.energy
        return rel_value, abs_value
