"""
Implements a controller for MATLAB Optimization Toolbox
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
import dill
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.utils.exceptions import CostFuncError

eng = matlab.engine.start_matlab()


class MatlabOptController(Controller):
    """
    Controller for MATLAB Optimization Toolbox, implementing lsqcurvefit
    """

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.support_for_bounds = True
        self.param_ranges = None
        self.initial_params_mat = None
        self.x_data_mat = None
        self.y_data_mat = None
        self._status = None
        self.result = None
        self.algorithm_check = {
            'all': ['levenberg-marquardt', 'trust-region-reflective'],
            'ls': ['levenberg-marquardt', 'trust-region-reflective'],
            'deriv_free': [],
            'general': []}

    def jacobian_information(self):
        """
        DFO cannot use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for Matlab fitting
        """
        if not isinstance(self.cost_func, create_cost_func('nlls')):
            raise CostFuncError('Matlab Optimization controller is not '
                                'compatible with the chosen cost function.')

        # Convert initial params into matlab array
        self.initial_params_mat = matlab.double([self.initial_params])
        self.x_data_mat = matlab.double(self.data_x.tolist())
        self.y_data_mat = matlab.double(self.data_y.tolist())

        # set matlab workspace variable for selected minimizer
        eng.workspace['minimizer'] = self.minimizer

        # set bounds if they have been set in problem definition file
        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            self.param_ranges = (matlab.double(lb), matlab.double(ub))
        else:
            # if no bounds are set, then pass empty arrays to
            # lsqcurvefit function
            self.param_ranges = (matlab.double([]), matlab.double([]))

        def _feval(p):
            """
            Function to call from matlab which evaluates the model
            """
            feval = self.problem.eval_model(p, x=self.data_x)
            return feval

        def _jeval(p):
            """
            Function to call from matlab which evaluates the jacobian
            """
            jeval = self.jacobian.eval(p)
            return jeval

        # serialize _feval and _jeval functions (if not using default
        # jacobian) and open within matlab engine so
        # matlab fitting function can be called
        temp_dir = TemporaryDirectory()
        feval_file = os.path.join(temp_dir.name, 'feval.pickle')
        with open(feval_file, 'wb') as f:
            dill.dump(_feval, f)
        eng.workspace['feval_file'] = feval_file
        eng.evalc('py_f = py.open(feval_file,"rb")')

        eng.evalc('eval_f = py.dill.load(py_f)')
        eng.evalc('py_f.close()')
        eng.evalc('f_wrapper = @(p, x)double(eval_f(p))')

        eng.workspace['eval_func'] = eng.workspace['f_wrapper']
        eng.evalc('options = optimoptions("lsqcurvefit", \
                                          "Algorithm", minimizer)')

        # if default jacobian is selected then pass _jeval function
        # to matlab
        if not self.jacobian.use_default_jac:
            jeval_file = os.path.join(temp_dir.name, 'jeval.pickle')
            with open(jeval_file, 'wb') as f:
                dill.dump(_jeval, f)
            eng.workspace['jeval_file'] = jeval_file
            eng.evalc('py_j = py.open(jeval_file,"rb")')

            eng.evalc('eval_j = py.dill.load(py_j)')
            eng.evalc('py_j.close()')

            eng.evalc('j_wrapper = @(p, x)double(eval_j(p))')

            eng.workspace['eval_func'] = [eng.workspace['f_wrapper'],
                                          eng.workspace['j_wrapper']]
            eng.evalc('options = \
                optimoptions("lsqcurvefit", \
                             "Algorithm", minimizer, \
                             "SpecifyObjectiveGradient", true)')

    def fit(self):
        """
        Run problem with Matlab
        """

        self.result, _, _, exitflag, _ = eng.lsqcurvefit(
            eng.workspace['eval_func'], self.initial_params_mat,
            self.x_data_mat, self.y_data_mat, self.param_ranges[0],
            self.param_ranges[1], eng.workspace['options'], nargout=5)
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
