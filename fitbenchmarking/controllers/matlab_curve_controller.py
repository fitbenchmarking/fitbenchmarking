"""
Implements a controller for MATLAB Curve Fitting Toolbox
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
    Controller for MATLAB Curve Fitting Toolbox fitting (fit)
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
        self.y_data_mat = None
        self.x_data_mat = None
        self.options = None
        self._status = None
        self.result = None
        self.algorithm_check = {
            'all': ['Trust-Region', 'Levenberg-Marquardt'],
            'ls': ['Trust-Region', 'Levenberg-Marquardt'],
            'deriv_free': [],
            'general': [],
            'simplex': [],
            'trust_region': ['Trust-Region', 'Levenberg-Marquardt'],
            'levenberg-marquardt': ['Levenberg-Marquardt'],
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
        self.y_data_mat = matlab.double(self.data_y.tolist())
        self.x_data_mat = matlab.double(self.data_x.tolist())

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

        eng.evalc("ft = fittype(@(p,x)eval_cost_mat(p))")

        self.options = eng.fitoptions('StartPoint', self.initial_params_mat,
                                      'Method', 'NonLinearLeastSquares',
                                      'Algorithm', self.minimizer)

    def fit(self):
        """
        Run problem with Matlab
        """
        [self.result, _, output] = eng.fit(self.x_data_mat,
                                           self.y_data_mat,
                                           eng.workspace['ft'],
                                           self.options, nargout=3)
        self._status = int(output.exitflag)

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
