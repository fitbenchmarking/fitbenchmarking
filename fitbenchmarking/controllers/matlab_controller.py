"""
Implements a controller for MATLAB
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
import dill
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller

eng = matlab.engine.start_matlab()


class MatlabController(Controller):
    """
    Controller for MATLAB fitting (fminsearch)
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
        self._status = None
        self.result = None
        self.algorithm_check = {
            'all': ['Nelder-Mead Simplex'],
            'ls': [None],
            'deriv_free': ['Nelder-Mead Simplex'],
            'general': ['Nelder-Mead Simplex'],
            'simplex': ['Nelder-Mead Simplex'],
            'trust_region': [],
            'levenberg-marquardt': [],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': []}

    def jacobian_information(self):
        """
        MATLAB cannot use Jacobian information
        """
        has_jacobian = False
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Convert initial params into matlab array
        self.initial_params_mat = matlab.double([self.initial_params])

        # clear out cached values
        self.cost_func.cache_cost_x = {'params': None, 'value': None}
        self.cost_func.cache_rx = {'params': None, 'value': None}

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        temp_dir = TemporaryDirectory()
        temp_file = os.path.join(temp_dir.name, 'temp.pickle')
        with open(temp_file, 'wb') as f:
            dill.dump(self.cost_func.eval_cost, f)
        eng.workspace['temp_file'] = temp_file
        eng.evalc('py_f = py.open(temp_file,"rb")')
        eng.evalc('eval_cost_mat = py.dill.load(py_f)')
        eng.evalc('py_f.close()')

    def fit(self):
        """
        Run problem with Matlab
        """
        [self.result, _, exitflag] = eng.fminsearch(
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
