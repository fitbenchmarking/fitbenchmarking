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

        # Workspace with data to fit
        self.fit_wks = None
        self.params = None
        self.errors = None

        # Time it took to run the Fit algorithm
        self.runtime = None

        # Best minimizer for a certain problem and its function definition
        self.minimizer = None
        self.ini_function_def = None
        self.fin_function_def = None

        self.comparison_mode = self.options.comparison_mode
        self.table_type = None
        self.value = None
        self.norm_value = None

    def __repr__(self):
        if self.comparison_mode == "abs":
            output = "{:.4g}".format(self.value)
        elif self.comparison_mode == "rel":
            output = "{:.4g}".format(self.value)
        elif self.comparison_mode == "both":
            output = "{:.4g} ({:.4g})".format(self.value, self.norm_value)
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
