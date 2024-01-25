"""
Emissions table
"""
from fitbenchmarking.results_processing.base_table import Table


class EmissionsTable(Table):
    r"""

    The emissions (kg CO\ :sub:`2`\ eq) results are calculated
    from an average (over num_runs) using the
    `codecarbon <https://mlco2.github.io/codecarbon/index.html>`_  module.
    num_runs is set in :ref:`options`.

    Configuration for codecarbon is set in ``.codecarbon.config``.

    Please note that for tracking CPU power usage on Windows or Mac,
    ``Intel Power Gadget`` shoud also be installed. For more information,
    see the Methodology section of the `codecarbon docs
    <https://mlco2.github.io/codecarbon/methodology.html#cpu>`_.

    """
    name = 'emissions'
    cbar_title = "Problem-Specific Cell Shading: Relative Emissions"

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
