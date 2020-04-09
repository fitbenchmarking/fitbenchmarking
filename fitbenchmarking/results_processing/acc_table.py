"""
Accuracy table
"""
import numpy as np
from fitbenchmarking.results_processing.base_table import Table


class AccTable(Table):
    """

    The accuracy results are calculated from the final chi squared value:

    .. math:: \\min_p \\sum_{i=1}^n \\left( \\frac{y_i - f(x_i, p)}{e_i} \\right)^2

    where :math:`n` data points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model function :math:`f(x,p)`.

    """

    def __init__(self, results, best_results, options, group_dir,
                 pp_locations):
        """
        Initialise accuracy table class.

        :param results: dictionary containing results, i.e.,
                           {'prob1': [result1, result2, ...],
                            'prob2': [result1, result2, ...], ...}
        :type results: dict
        :param options: The options used in the fitting problem and plotting
        :type options: fitbenchmarking.utils.options.Options
        """
        self.name = 'acc'
        super(AccTable, self).__init__(
            results, best_results, options, group_dir, pp_locations)

        self.has_pp = True
        self.pp_filenames = [self.pp_locations[0]]

    def get_values(self):
        colour = {}
        abs_value = {}
        rel_value = {}
        links = {}
        for key, value in self.results_dict.items():
            abs_value[key] = [v.chi_sq for v in value]
            min_value = np.min(abs_value[key])
            rel_value[key] = [v.chi_sq / min_value for v in value]
            colour_index = np.searchsorted(self.colour_bounds, rel_value[key])
            colour[key] = [self.html_colours[i] for i in colour_index]
            links[key] = [v.support_page_link for v in value]

        return abs_value, rel_value, colour, links
