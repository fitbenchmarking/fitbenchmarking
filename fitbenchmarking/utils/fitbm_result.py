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
            output = "{:.4g} ({:.4g})".format(self.value, self.norm_value)
        return output

    def set_return_value(self):
        """
        Utility function set values for the tables
        """
        if self.table_type == "runtime":
            self.value = self.runtime
            self.norm_value = self.norm_runtime
            self.colour = self.colour_runtime
        if self.table_type == "chi_sq":
            self.value = self.chi_sq
            self.norm_value = self.norm_chi_sq
            self.colour = self.colour_chi_sq

    def set_colour_scale(self):
        """
        Utility function set colour rendering for html tables
        """
        colour_scale = self.options.colour_scale
        colour_bounds = [colour[0] for colour in colour_scale]
        # prepending 0 value for colour bound
        colour_bounds = [0] + colour_bounds
        html_colours = [colour[2] for colour in colour_scale]
        self.colour_runtime = colour_scale[-1]
        self.colour_chi_sq = colour_scale[-1]
        for i in range(len(colour_bounds)):
            if colour_bounds[i] <= self.norm_runtime < colour_bounds[i + 1]:
                self.colour_runtime = html_colours[i]
            if colour_bounds[i] <= self.norm_chi_sq < colour_bounds[i + 1]:
                self.colour_chi_sq = html_colours[i]

    def set_normalised_data(self):
        """
        Utility function that sets the normalised runtime and accuracy values
        """
        try:
            self.norm_chi_sq = self.chi_sq / self.min_chi_sq
        except Exception as excp:
            print(str(excp))

        try:
            self.norm_runtime = self.runtime / self.min_runtime
        except Exception as excp:
            print(str(excp))
