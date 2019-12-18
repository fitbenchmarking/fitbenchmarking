from __future__ import (absolute_import, division, print_function)

import numpy as np


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options=None, problem=None, fit_status=None,
                 chi_sq=None, fit_wks=None, params=None, errors=None,
                 runtime=None, minimizer=None, ini_function_def=None,
                 fin_function_def=None):
        self.options = options
        self.problem = problem
        self.fit_status = fit_status
        self.chi_sq = chi_sq
        self._min_chi_sq = None
        # Workspace with data to fit
        self.fit_wks = fit_wks
        self.params = params
        self.errors = errors

        # Time it took to run the Fit algorithm
        self.runtime = runtime
        self._min_runtime = None

        # Best minimizer for a certain problem and its function definition
        self.minimizer = minimizer
        self.ini_function_def = ini_function_def
        self.fin_function_def = fin_function_def

        self.value = None
        self.norm_value = None

        self.colour = None
        self.colour_runtime = None
        self.colour_acc = None

        # Defines the type of table to be produced
        self._table_type = None

    def __str__(self):
        if self.table_type is not None:
            if self.table_type == "compare":
                output = "{:.4g} ({:.4g})<br>{:.4g} ({:.4g})".format(
                    self.chi_sq, self.norm_acc,
                    self.runtime, self.norm_runtime)
            else:
                if self.options.comparison_mode == "abs":
                    output = "{:.4g}".format(self.value)
                elif self.options.comparison_mode == "rel":
                    output = "{:.4g}".format(self.value)
                elif self.options.comparison_mode == "both":
                    output = "{:.4g} ({:.4g})".format(self.value,
                                                      self.norm_value)
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
        elif value == "acc":
            self.value = self.chi_sq
            self.norm_value = self.norm_acc
            self.colour = self.colour_acc
        elif value == "compare":
            self.colour = [self.colour_acc, self.colour_runtime]

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

    @property
    def min_chi_sq(self):
        return self._min_chi_sq

    @min_chi_sq.setter
    def min_chi_sq(self, value):
        self._min_chi_sq = value
        if not self.chi_sq > 0:
            self.chi_sq = np.inf
        self.norm_acc = self.chi_sq / self.min_chi_sq

    @property
    def min_runtime(self):
        return self._min_runtime

    @min_runtime.setter
    def min_runtime(self, value):
        self._min_runtime = value
        self.norm_runtime = self.runtime / self.min_runtime
