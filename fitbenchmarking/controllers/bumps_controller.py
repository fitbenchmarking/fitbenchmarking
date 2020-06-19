"""
Implements a controller for the Bumps fitting software.
"""

from bumps.fitters import fit as bumpsFit
from bumps.names import Curve, FitProblem

import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class BumpsController(Controller):
    """
    Controller for the Bumps fitting software.

    Sasview requires a model to fit.
    Setup creates a model with the correct function.
    """

    def __init__(self, problem):
        """
        Extract param names for function setup

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(BumpsController, self).__init__(problem)

        self._param_names = self.problem.param_names

        self._func_wrapper = None
        self._fit_problem = None
        self._bumps_result = None
        self.algorithm_check = {
            'all': ['amoeba', 'lm-bumps', 'newton', 'de', 'mp'],
            'ls': ['lm-bumps', 'mp'],
            'deriv_free': ['amoeba', 'de'],
            'general': ['amoeba', 'newton', 'de']}

    def setup(self):
        """
        Setup problem ready to run with Bumps.

        Creates a FitProblem for calling in the fit() function of Bumps
        """
        # Bumps fails with the *args notation
        param_name_str = ', '.join(self._param_names)
        wrapper = "def fitFunction(x, {}):\n".format(param_name_str)
        wrapper += "    return func(x, {})".format(param_name_str)

        exec_dict = {'func': self.problem.function}
        exec(wrapper, exec_dict)

        model = exec_dict['fitFunction']

        # Remove any function attribute. BinWidth is the only attribute in all
        # FitBenchmark (Mantid) problems.
        param_dict = {name: value
                      for name, value
                      in zip(self._param_names, self.initial_params)}

        # Create a Function Wrapper for the problem function. The type of the
        # Function Wrapper is acceptable by Bumps.
        func_wrapper = Curve(fn=model,
                             x=self.data_x,
                             y=self.data_y,
                             dy=self.data_e,
                             **param_dict)

        # Set a range for each parameter
        val_ranges = self.problem.value_ranges
        for name in self._param_names:
            min_val = -np.inf
            max_val = np.inf
            if val_ranges is not None and name in val_ranges:
                min_val = val_ranges[name][0]
                max_val = val_ranges[name][1]
            func_wrapper.__dict__[name].range(min_val, max_val)

        # Create a Problem Wrapper. The type of the Problem Wrapper is
        # acceptable by Bumps fitting.
        self._func_wrapper = func_wrapper
        self._fit_problem = FitProblem(func_wrapper)
        if self.minimizer == "lm-bumps":
            self.minimizer = "lm"

    def fit(self):
        """
        Run problem with Bumps.
        """
        result = bumpsFit(self._fit_problem, method=self.minimizer)

        self._bumps_result = result
        self._status = self._bumps_result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 2:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._bumps_result.x
