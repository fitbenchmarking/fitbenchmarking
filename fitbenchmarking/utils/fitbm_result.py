from __future__ import (absolute_import, division, print_function)


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self):
        self.options = None
        self.problem = None
        self.fit_status = None
        self.chi_sq = None
        self.min_chi_sq = None
        # Workspace with data to fit
        self.fit_wks = None
        self.params = None
        self.errors = None

        # Time it took to run the Fit algorithm
        self.runtime = None
        self.min_chi_sq = None

        # Best minimizer for a certain problem and its function definition
        self.minimizer = None
        self.ini_function_def = None
        self.fin_function_def = None

        self.table_type = None
        self.value = 1
        self.norm_value = 1

    def __repr__(self):
        if self.options.comparison_mode == "abs":
            output = "{:.4g}".format(self.value)
        elif self.options.comparison_mode == "rel":
            output = "{:.4g}".format(self.value)
        elif self.options.comparison_mode == "both":
            output = "{:.4g} ({:.4g})".format(
                self.chi_sq, self.chi_sq / self.min_chi_sq)
        return output

    def set_return_value(self):
        """
        Utility function set values for the tables

        :return: tuple(value, norm_value) chi_sq or runtime value
                 together with the corresponding normalised value
        :rtype: (float, float)
        """
        if self.table_type == "runtime":
            self.value = self.runtime
            self.norm_value = self.norm_runtime
        if self.table_type == "chi_sq":
            self.value = self.chi_sq
            self.norm_value = self.norm_chi_sq
