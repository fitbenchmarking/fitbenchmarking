"""
Implements a controller for MATLAB
"""
import matlab

from fitbenchmarking.controllers.base_controller import Controller
# from fitbenchmarking.controllers.matlab_mixin import MatlabMixin
from fitbenchmarking.extern import matlab_controller_c as mc


class MatlabController(Controller):
    """
    Controller for MATLAB fitting (fminsearch)
    """

    algorithm_check = {
        'all': ['Nelder-Mead Simplex'],
        'ls': [],
        'deriv_free': ['Nelder-Mead Simplex'],
        'general': ['Nelder-Mead Simplex'],
        'simplex': ['Nelder-Mead Simplex'],
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
        # Convert initial params into matlab array
        #self.initial_params_mat = matlab.double([self.initial_params])

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        #self.eng.workspace['eval_cost_mat'] = self.py_to_mat('eval_cost')
        mc.init(self.cost_func.eval_cost, len(self.initial_params))

    def fit(self):
        """
        Run problem with Matlab
        """
        # [self.result, _, exitflag] = self.eng.fminsearch(
        #     self.eng.workspace['eval_cost_mat'],
        #     self.initial_params_mat, nargout=3)
        [self.result, exitflag] = mc.fit(self.initial_params)
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

        mc.cleanup()
        self.final_params = self.result
