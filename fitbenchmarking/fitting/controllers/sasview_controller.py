"""
Implements a controller for the SasView fitting software.
"""

from bumps.fitters import fit as bumpsFit
from bumps.names import Curve, FitProblem

import numpy as np

from fitbenchmarking.fitting.controllers.base_controller import Controller


class SasviewController(Controller):
    """
    Controller for the Sasview fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Extract param names for function setup
        """
        super(SasviewController, self).__init__(problem, use_errors)

        self._param_names = [param[0] for param in problem.starting_values]

        self._func_wrapper = None
        self._fit_problem = None
        self._bumps_results = None

    def setup(self):
        """
        Setup problem ready to run with SasView.

        Creates a Sasview FitProblem for calling in fit()
        """
        # Bumps fails with the *args notation
        param_name_str = ', '.join(self._param_names)
        wrapper = "def fitFunction(x, {}):\n".format(param_name_str)
        wrapper += "    return func(x, {})".format(param_name_str)

        exec_dict = {'func': self.functions[self.function_id][0]}
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
        val_ranges = self.problem.starting_value_ranges
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
        Run problem with SasView.
        """
        result = bumpsFit(self._fit_problem, method=self.minimizer)

        self.success = result.success
        self._bumps_result = result

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        self.final_params = self._bumps_result.x
        self.results = self._func_wrapper.theory()
