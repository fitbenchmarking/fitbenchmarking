"""
Implements a controller to the lm implementation in Herbert/Horace
"""

import matlab.engine
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class HoraceController(MatlabMixin, Controller):
    """
    Controlller for fit in Herbert
    """

    algorithm_check = {
            'all': ['lm-lsqr'],
            'ls': ['lm-lsqr'],
            'deriv_free': ['lm-lsqr'],
            'general': [],
            'simplex': [],
            'trust_region': [],
            'levenberg-marquardt': ['lm-lsqr'],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': []}

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

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Initialize Horace in the Matlab engine
        eng.evalc('horace_on')

        # Convert initial params into matlab array
        eng.workspace['x_mat'] = matlab.double(
            self.data_x.tolist())
        eng.workspace['y_mat'] = matlab.double(
            np.zeros(self.data_y.shape).tolist())
        eng.workspace['e_mat'] = matlab.double(
            np.ones(self.data_y.shape).tolist())
        eng.evalc("W = struct('x', x_mat, 'y', y_mat, 'e', e_mat)")
        eng.workspace['initial_params'] = matlab.double(
            [self.initial_params])

        # serialize cost_func.eval_r and open within matlab engine
        # so that matlab fitting function can be called
        eng.workspace['eval_f'] = self.py_to_mat(self.cost_func.eval_r, eng)
        eng.evalc('f_wrapper = @(x, p) double(eval_f(p))')

        # Setup the timer to track using calls to eval_f
        self.setup_timer('eval_f', eng)

        # Setup multifit data structures
        eng.evalc('kk = multifit(W)')
        eng.evalc('kk = kk.set_fun(f_wrapper)')
        eng.evalc('kk = kk.set_pin(initial_params)')

    def fit(self):
        """
        Run problem with Horace
        """
        eng.evalc('[fitted_data, fit_params] = kk.fit')
        self._status = int(eng.workspace['fit_params']['converged'])

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 2
        else:
            self.flag = 0

        self.final_params = eng.workspace['fit_params']['p'][0]