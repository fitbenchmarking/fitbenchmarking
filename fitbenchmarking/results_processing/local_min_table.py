"""
compare table
"""
import matplotlib.colors as clrs
import numpy as np

from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.results_processing.base_table import (Table,
                                                           CONTRAST_RATIO_AAA,
                                                           background_to_text)
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
    name = 'local_min'
    cbar_title = "Cell Shading: Minimum Found"

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
        :param pp_locations: the locations of the performance profiles
        :type pp_locations: dict[str,str]
        :param table_name: Name of the table
        :type table_name: str
        """
        super().__init__(results, best_results, options, group_dir,
                         pp_locations, table_name)
        self.pps = ['acc', 'runtime']

        # Check whether any selected cost function is not a least squares
        # problem - if non least squares are present then local min table is
        # not appropriate and option should be ignored
        for cf in options.cost_func_type:
            if not issubclass(create_cost_func(cf), BaseNLLSCostFunc):
                raise IncompatibleTableError(
                    "The local_min table cannot be produced with the "
                    f"{cf} cost function. As a result, "
                    "this table will not be produced.")

        self.cbar_left_label = "True"
        self.cbar_right_label = "False"

    def get_value(self, result):
        """
        Gets the main value to be reported in the tables for a given result

        Note that the first value (relative accuracy) will be used in the
        default colour handling.

        :param result: The result to generate the values for.
        :type result: FittingResult

        :return: Whether the minimizer found a local minimizer (under the tests
                 specified above) and :math:`\\frac{|| J^T r||}{||r||}`
        :rtype: bool, float
        """

        res = result.r_x

        jac = result.jac_x

        if res is None:
            return None, None

        if result.params is None:
            return False, np.inf

        min_test = res.dot(jac)
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

        :return: Colours as hex strings for each input value and
                 Foreground colours for the text as html rgb strings
                 e.g. 'rgb(255, 255, 255)'
        :rtype: tuple[list[str], list[str]]
        """
        rgba = cmap([cmap_range[0] if local_min else cmap_range[1]
                     for local_min in vals])
        hex_strs = [clrs.rgb2hex(colour) for colour in rgba]
        text_str = [background_to_text(colour[:3], CONTRAST_RATIO_AAA)
                    for colour in rgba]
        return hex_strs, text_str

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
        if local_min is None:
            return 'N/A'
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

    @classmethod
    def get_error_str(cls, result, *args, **kwargs):
        """
        Get the error string for a result based on error_template
        This can be overridden if tables require different error formatting.

        :param result: The result to get the error string for
        :type result: FittingResult

        :return: A string representation of the error
        :rtype: str
        """
        if result.r_x is None:
            return ''
        return super().get_error_str(result, *args, **kwargs)

    def get_description(self):
        """
        Generates table description from class docstrings and converts them
        into html

        :return: Dictionary containing table descriptions
        :rtype: dict
        """
        html = super().get_description()
        html['local_min_mode'] = '"N/A" in the table indicates that the ' \
            'cost function does not provide residuals.'

        return html
