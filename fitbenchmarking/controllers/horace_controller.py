"""
Implements a controller to the lm implementation in Herbert/Horace
"""

import matlab
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin


class HoraceController(MatlabMixin, Controller):
    """
    Controller for fit in Herbert
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
        self._fit_params = None

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Initialize Horace in the Matlab engine
        self.eng.evalc('horace_on')

        # Convert initial params into matlab array
        self.eng.workspace['x_mat'] = matlab.double(
            self.data_x.tolist())
        self.eng.workspace['y_mat'] = matlab.double(
            np.zeros(self.data_y.shape).tolist())
        self.eng.workspace['e_mat'] = matlab.double(
            np.ones(self.data_y.shape).tolist())
        self.eng.evalc("W = struct('x', x_mat, 'y', y_mat, 'e', e_mat)")
        self.eng.workspace['initial_params'] = matlab.double(
            [self.initial_params])

        # serialize cost_func.eval_r and open within matlab engine
        # so that matlab fitting function can be called
        self.eng.workspace['eval_f'] = self.py_to_mat('eval_r')
        self.eng.evalc('f_wrapper = @(x, p) double(eval_f(p))')

        # Setup multifit data structures
        self.eng.evalc('kk = multifit(W)')
        self.eng.evalc('kk = kk.set_fun(f_wrapper)')
        self.eng.evalc('kk = kk.set_pin(initial_params)')

    def fit(self):
        """
        Run problem with Horace
        """
        self.eng.evalc('[fitted_data, fit_params] = kk.fit')
        self._fit_params = self.eng.workspace['fit_params']

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if int(self._fit_params['converged']) == 0:
            self.flag = 2
        else:
            self.flag = 0

        self.final_params = np.array(self._fit_params['p'][0], dtype= np.float64).flatten()

        # Allow repeat calls to cleanup without falling over
        # try:
        #     self.eng.evalc(
        #         'if not(any(cellfun(@(x) x=="horace", persistent_vars)));'
        #         ' horace_off;'
        #         'end;'
        #     )
        # except matlab.engine.MatlabExecutionError:
        #     pass
