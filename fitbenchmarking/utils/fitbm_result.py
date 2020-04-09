from __future__ import (absolute_import, division, print_function)

import os

import numpy as np

GRAD_TOL = 1e-1
RES_TOL = 1e-8


class FittingResult(object):
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options=None, problem=None, fit_status=None,
                 chi_sq=None, params=None, runtime=None, minimizer=None,
                 ini_function_params=None, fin_function_params=None,
                 error_flag=None):

        self.options = options
        self.problem = problem
        self.fit_status = fit_status
        self.params = params

        self.chi_sq = chi_sq

        # Time it took to run the Fit algorithm
        self.runtime = runtime

        # Minimizer for a certain problem and its function definition
        self.minimizer = minimizer
        self.ini_function_params = ini_function_params
        self.fin_function_params = fin_function_params

        # Controller error handling
        self.error_flag = error_flag

        # Paths to various output files
        self.support_page_link = ''
        self.start_figure_link = ''
        self.figure_link = ''

        # Error written to support page if plotting failed
        # Default can be overwritten with more information
        self.figure_error = 'Plotting Failed'

        self._norm_acc = None
        self._norm_runtime = None
        self.is_best_fit = False

    @property
    def norm_acc(self):
        if self._norm_acc is None:
            self._norm_acc = self.chi_sq / self.min_chi_sq
        return self._norm_acc

    @norm_acc.setter
    def norm_acc(self, value):
        """
        Stores the normalised accuracy and updates the value

        :param value: New value for norm_runtime
        :type value: float
        """
        self._norm_acc = value

    @property
    def norm_runtime(self):
        if self._norm_runtime is None:
            self._norm_runtime = self.runtime / self.min_runtime
        return self._norm_runtime

    @norm_runtime.setter
    def norm_runtime(self, value):
        """
        Stores the normalised runtime and updates the value

        :param value: New value for norm_runtime
        :type value: float
        """
        self._norm_runtime = value
