from __future__ import (absolute_import, division, print_function)

import numpy as np


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

        # Best minimizer for a certain problem and its function definition
        self.minimizer = None
        self.ini_function_def = None
        self.fin_function_def = None

        self.value = None
        self.norm_value = None
        self.colour = None
        self.colour_runtime = None
        self.colour_acc = None

        # Defines the type of table to be produced
        self._table_type = None

    def __str__(self):
        if self.table_type is not None:
            if self.options.comparison_mode == "abs":
                output = "{:.4g}".format(self.value)
            elif self.options.comparison_mode == "rel":
                output = "{:.4g}".format(self.value)
            elif self.options.comparison_mode == "both":
                output = "{:.4g} ({:.4g})".format(self.value, self.norm_value)
        else:
            output = 'Fitting problem class: minimizer = {0}'.format(
                self.minimizer)
        return output

    @property
    def table_type(self):
        return self._table_type

    @table_type.setter
    def table_type(self, value):
        self._table_type = value
        if value == "runtime":
            self.value = self.runtime
            self.norm_value = self.norm_runtime
            self.colour = self.colour_runtime
        if value == "acc":
            self.value = self.chi_sq
            self.norm_value = self.norm_acc
            self.colour = self.colour_acc

    def set_colour_scale(self):
        """
        Utility function set colour rendering for html tables
        """
        colour_scale = self.options.colour_scale
        colour_bounds = [colour[0] for colour in colour_scale]
        # prepending 0 value for colour bound
        colour_bounds = [0] + colour_bounds
        html_colours = [colour[1] for colour in colour_scale]
        self.colour_runtime = colour_scale[-1]
        self.colour_acc = colour_scale[-1]
        for i in range(len(colour_bounds) - 1):
            if colour_bounds[i] < self.norm_runtime <= colour_bounds[i + 1]:
                self.colour_runtime = html_colours[i]
            if colour_bounds[i] < self.norm_acc <= colour_bounds[i + 1]:
                self.colour_acc = html_colours[i]

    def set_normalised_data(self):
        """
        Utility function that sets the normalised runtime and accuracy values
        """
        try:
            if not self.chi_sq > 0:
                self.chi_sq = np.inf
            self.norm_acc = self.chi_sq / self.min_chi_sq
        except Exception as excp:
            print(str(excp))

        try:
            self.norm_runtime = self.runtime / self.min_runtime
        except Exception as excp:
            print(str(excp))
