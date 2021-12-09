"""
Implements a controller for MATLAB Statistics Toolbox
"""

import matlab.engine
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class MatlabStatsController(MatlabMixin, Controller):
    """
    Controller for MATLAB Statistics Toolbox fitting (nlinfit)
    """

    algorithm_check = {
        'all': ['Levenberg-Marquardt'],
        'ls': ['Levenberg-Marquardt'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': ['Levenberg-Marquardt'],
        'levenberg-marquardt': ['Levenberg-Marquardt'],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': []}

    controller_name = 'matlab_stats'

    incompatible_problems = ['mantid']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.x_data_mat = None
        self.y_data_mat = None
        self._status = None
        self.result = None

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Convert initial params into matlab array
        self.y_data_mat = matlab.double(np.zeros(self.data_y.shape).tolist())
        self.initial_params_mat = matlab.double([self.initial_params])
        self.x_data_mat = matlab.double(self.data_x.tolist())

        # serialize cost_func.eval_r and open within matlab engine
        # so that matlab fitting function can be called
        eng.workspace['eval_f'] = self.py_to_mat(self.cost_func.eval_r, eng)
        eng.evalc('f_wrapper = @(p, x)double(eval_f(p))')

    def fit(self):
        """
        Run problem with Matlab Statistics Toolbox
        """

        self.result = eng.nlinfit(self.x_data_mat, self.y_data_mat,
                                  eng.workspace['f_wrapper'],
                                  self.initial_params_mat, nargout=1)
        self._status = 0 if self.result is not None else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        else:
            self.flag = 2

        self.final_params = self.result[0]
