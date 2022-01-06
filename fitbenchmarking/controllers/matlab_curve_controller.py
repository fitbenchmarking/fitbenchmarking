"""
Implements a controller for MATLAB Curve Fitting Toolbox
"""
import numpy as np
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class MatlabCurveController(MatlabMixin, Controller):
    """
    Controller for MATLAB Curve Fitting Toolbox fitting (fit)
    """

    algorithm_check = {
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
        self.support_for_bounds = True
        self.options = None
        self._status = None
        self.result = None

    controller_name = 'matlab_curve'

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Convert initial params into matlab array
        self.initial_params_mat = matlab.double(list(self.initial_params))
        eng.workspace['x_data'] = matlab.double(self.data_x.tolist())
        eng.workspace['y_data'] = matlab.double(self.data_y.tolist())

        def wrapper(x, y, *p):

            kwargs = {"x": np.array(x),
                      "y": np.array(y)}

            # To avoid errors in fittype function evaluation, if e is
            # not the same length as y, then replace e with an array
            # of ones
            if self.data_e is not None and len(self.data_e) != len(y):
                kwargs["e"] = np.ones(len(y))

            result = self.cost_func.eval_r(p, **kwargs)

            return result

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        eng.workspace['eval_cost_mat'] =\
            self.py_to_mat(wrapper, eng)

        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            eng.workspace['lower_bounds'] = matlab.double(lb)
            eng.workspace['upper_bounds'] = matlab.double(ub)
        else:
            # if no bounds are set, then pass empty arrays to
            # fitoptions function
            eng.workspace['lower_bounds'] = matlab.double([])
            eng.workspace['upper_bounds'] = matlab.double([])

        params = self.problem.param_names
        eng.workspace['init_params'] = self.initial_params_mat
        eng.evalc("opts = fitoptions('StartPoint', init_params,"
                  "'Method', 'NonLinearLeastSquares',"
                  f"'Algorithm', '{self.minimizer}',"
                  "'Lower', lower_bounds,"
                  "'Upper', upper_bounds)")

        eng.evalc(f"ft = fittype(@({', '.join(params)}, x, y)"
                  f"double(eval_cost_mat(x, y, {', '.join(params)}))',"
                  f"'options', opts, 'independent', {{'x', 'y'}},"
                  "'dependent', 'z')")

    def fit(self):
        """
        Run problem with Matlab
        """
        eng.evalc("[fitobj, gof, output] = fit([x_data', y_data'],"
                  "zeros(size(x_data))', ft)")
        self._status = int(eng.workspace['output']['exitflag'])

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

        self.final_params = eng.coeffvalues(eng.workspace['fitobj'])[0]
