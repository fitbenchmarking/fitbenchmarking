"""
Implements a controller for MATLAB Optimization Toolbox
"""

import matlab.engine
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class MatlabOptController(MatlabMixin, Controller):
    """
    Controller for MATLAB Optimization Toolbox, implementing lsqcurvefit
    """

    algorithm_check = {
        'all': ['levenberg-marquardt', 'trust-region-reflective'],
        'ls': ['levenberg-marquardt', 'trust-region-reflective'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': ['levenberg-marquardt', 'trust-region-reflective'],
        'levenberg-marquardt': ['levenberg-marquardt'],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': []}

    jacobian_enabled_solvers = ['levenberg-marquardt',
                                'trust-region-reflective']

    controller_name = 'matlab_opt'

    incompatible_problems = ['mantid']

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
        self.x_data_mat = None
        self.y_data_mat = None
        self._status = None
        self.result = None

    def setup(self):
        """
        Setup for Matlab Optimization Toolbox fitting
        """

        # Convert initial params into matlab array
        self.y_data_mat = matlab.double(np.zeros(self.data_y.shape).tolist())
        self.initial_params_mat = matlab.double([self.initial_params])
        self.x_data_mat = matlab.double(self.data_x.tolist())

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

        # serialize cost_func.eval_r and jacobian.eval (if not
        # using default jacobian) and open within matlab engine
        # so matlab fitting function can be called
        eng.workspace['eval_f'] = self.py_to_mat(self.cost_func.eval_r, eng)
        eng.evalc('f_wrapper = @(p, x)double(eval_f(p))')

        eng.workspace['init'] = self.initial_params_mat
        eng.workspace['x'] = self.x_data_mat
        print(eng.eval('f_wrapper(init, x)'))

        # if default jacobian is not selected then pass _jeval
        # function to matlab
        if not self.cost_func.jacobian.use_default_jac:
            eng.workspace['eval_j'] = self.py_to_mat(self.cost_func.jac_res,
                                                     eng)
            eng.evalc('j_wrapper = @(p, x)double(eval_j(p))')

            eng.workspace['eval_func'] = [eng.workspace['f_wrapper'],
                                          eng.workspace['j_wrapper']]
            eng.evalc('options = \
                optimoptions("lsqcurvefit", \
                             "Algorithm", minimizer, \
                             "SpecifyObjectiveGradient", true)')
        else:
            eng.workspace['eval_func'] = eng.workspace['f_wrapper']
            eng.evalc('options = optimoptions("lsqcurvefit", \
                                          "Algorithm", minimizer)')

    def fit(self):
        """
        Run problem with Matlab Optimization Toolbox
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
