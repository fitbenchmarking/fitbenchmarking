"""
compare table
"""
import os

import matplotlib.colors as clrs
import numpy as np

from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.results_processing.base_table import Table
from fitbenchmarking.utils.exceptions import IncompatibleTableError

GRAD_TOL = 1e-1
RES_TOL = 1e-8


class LocalMinTable(Table):
    """

    The local min results shows a ``True`` or ``False`` value together with
    :math:`\\frac{|| J^T r||}{||r||}`. The ``True`` or ``False`` indicates
    whether the software finds a minimum with respect to the following
    criteria:


    - :math:`||r|| \\leq` RES\\_TOL,
    - :math:`|| J^T r|| \\leq` GRAD\\_TOL,
    - :math:`\\frac{|| J^T r||}{||r||} \\leq` GRAD\\_TOL,

    where :math:`J` and :math:`r` are the Jacobian and residual of
    :math:`f(x, p)`, respectively. The tolerances can be found in the results
    object.

    """

    def __init__(self, results, best_results, options, group_dir, pp_locations,
                 table_name):
        """
        Initialise the local minimizer table which shows given the
        conditioners stated in the doc string whether the final parameters
        are a local minimum

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
        self.name = 'local_min'

        self.has_pp = True
        self.pp_filenames = \
            [os.path.relpath(pp, group_dir) for pp in pp_locations]

        # Check whether any selected cost function is not a least squares
        # problem - if non least squares are present then local min table is
        # not appropriate and option should be ignored
        for cf in options.cost_func_type:
            if not issubclass(create_cost_func(cf), BaseNLLSCostFunc):
                raise IncompatibleTableError(
                    "The local_min table cannot be produced with the "
                    f"{cf} cost function. As a result, "
                    "this table will not be produced.")

        self.cbar_title = "Cell Shading: Minimum Found"
        self.cbar_left_label = "True"
        self.cbar_right_label = "False"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative chi_sq) will be used in the default
        colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: Whether the minimizer found a local minimizer (under the tests
                 specified above) and :math:`\\frac{|| J^T r||}{||r||}`
        :rtype: bool, float
        """
        if result.params is None:
            return False, np.inf

        res = result.cost_func.eval_r(result.params,
                                      x=result.data_x,
                                      y=result.data_y,
                                      e=result.data_e)

        jac = result.cost_func.jac_res(result.params,
                                       x=result.data_x,
                                       y=result.data_y,
                                       e=result.data_e)

        min_test = np.matmul(res, jac)
        norm_r = np.linalg.norm(res)
        norm_min_test = np.linalg.norm(min_test)

        if result.error_flag != 5:
            norm_rel = norm_min_test / norm_r
        else:
            norm_rel = np.inf

        local_min = any([norm_r <= RES_TOL,
                         norm_min_test <= GRAD_TOL,
                         norm_rel <= GRAD_TOL])

        return local_min, norm_rel

    @staticmethod
    def vals_to_colour(vals, cmap, cmap_range, log_ulim):
        # pylint: disable=unused-argument
        """
        Converts an array of values to a list of hexadecimal colour strings
        using sampling from a matplotlib colourmap according to whether a
        minimum was found.

        Set to the bottom of the range if minimum was found, otherwise set to
        the top of the range.

        :param vals: values in the range [0, 1] to convert to colour strings
        :type vals: list[float]
        :param cmap: matplotlib colourmap
        :type cmap: matplotlib colourmap object
        :param cmap_range: values in range [0, 1] for colourmap cropping
        :type cmap_range: list[float], 2 elements
        :param log_ulim: **Unused** log10 of worst shading cutoff value
        :type log_ulim: float

        :return: colours as hex strings for each input value
        :rtype: list[str]
        """
        rgba = cmap([cmap_range[0] if local_min else cmap_range[1]
                     for local_min in vals])
        return [clrs.rgb2hex(colour) for colour in rgba]

    def display_str(self, value):
        """
        Combine the boolean value from variable local_min with the
        normalised residual

        :param value: Whether the minimizer found a local minimizer and the
                      :math:`\\frac{|| J^T r||}{||r||}` value
        :type value: bool, float

        :return: string representation of the value for display in the table.
        :rtype: str
        """
        local_min, norm_rel = value
        template = self.output_string_type['abs']
        return f'{str(local_min)} ({template.format(norm_rel)})'

    def save_colourbar(self, fig_dir, n_divs=2, sz_in=None) -> str:
        # pylint: disable=unused-argument
        """
        Override default save_colourbar as there are only 2 possible divisions
        of the colour map (true or false).

        :param fig_dir: path to figures directory
        :type fig_dir: str
        :param n_divs: **Unused** number of divisions of shading in colourbar
        :type n_divs: int, Fixed to 2
        :param sz_in: dimensions of png in inches [width, height]
        :type sz_in: list[float] - 2 elements

        :return: The relative path to the colourbar image.
        :rtype: str
        """
        if sz_in is not None:
            return super().save_colourbar(fig_dir, n_divs=2, sz_in=sz_in)
        return super().save_colourbar(fig_dir, n_divs=2)
