"""
Implements a controller for MATLAB Statistics Toolbox
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
import numpy as np
import dill
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller

eng = matlab.engine.start_matlab()


class MatlabStatsController(Controller):
    """
    Controller for MATLAB Statistics Toolbox fitting (nlinfit)
    """

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.initial_params_mat = None
        self.x_data_mat = None
        self.y_data_mat = None
        self._status = None
        self.result = None
        self.algorithm_check = {
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
            'steepest_descent': []}

    def jacobian_information(self):
        """
        MATLAB Statistics Toolbox cannot use external Jacobian information
        """
        has_jacobian = False
        jacobian_free_solvers = ['Levenberg-Marquardt']
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Convert initial params into matlab array
        self.y_data_mat = matlab.double(np.zeros(self.data_y.shape).tolist())
        self.initial_params_mat = matlab.double([self.initial_params])
        self.x_data_mat = matlab.double(self.data_x.tolist())

        def _feval(p):
            """
            Function to call from matlab which evaluates the residuals
            """
            feval = -self.cost_func.eval_r(p)
            return feval

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        temp_dir = TemporaryDirectory()
        temp_file = os.path.join(temp_dir.name, 'temp.pickle')
        with open(temp_file, 'wb') as f:
            dill.dump(_feval, f)
        eng.workspace['temp_file'] = temp_file
        eng.evalc('py_f = py.open(temp_file,"rb")')
        eng.evalc('eval_f = py.dill.load(py_f)')
        eng.evalc('py_f.close()')
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
