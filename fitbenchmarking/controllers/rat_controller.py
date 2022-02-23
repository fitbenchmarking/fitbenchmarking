"""
Implements a controller for the matlab RAT package
"""
import os

import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class RATController(MatlabMixin, Controller):
    """
    Controller for MATLAB fitting (fminsearch)
    """

    algorithm_check = {
        'all': ['fminsearch'],
        'ls': [],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': [],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': [],
    }

    incompatible_problems = ['mantid']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self._status = None
        self.result = None

    def setup(self):
        """
        Setup for Matlab fitting
        """
        for path in self.problem.options.matlab_path:
            eng.addpath(path)
        RAT_root = os.path.dirname(eng.which('addRatPaths'))
        cwd = eng.cd(RAT_root)
        eng.evalc('addRatPaths;')
        eng.evalc("setappdata(0,'ratOut', {0; 0})")
        _ = eng.cd(cwd)
        # Convert initial params into matlab array
        eng.workspace['initial_params_mat'] = self.initial_params
        self.initial_params_mat = matlab.double([self.initial_params])

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        eng.workspace['eval_cost_mat'] =\
            self.py_to_mat(self.cost_func.eval_cost, eng)

    def fit(self):
        """
        Run problem with Matlab
        """
        [self.result, _, exitflag] = eng.ratFminsearch(
            eng.workspace['eval_cost_mat'],
            self.initial_params_mat, nargout=3)
        self._status = int(exitflag)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 1:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self.result[0]
