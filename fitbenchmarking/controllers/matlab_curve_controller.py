"""
Implements a controller for MATLAB Curve Fitting Toolbox
"""
import numpy as np
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin

eng = matlab.engine.start_matlab()


class MatlabController(MatlabMixin, Controller):
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
        self.initial_params_mat = matlab.double(list(self.initial_params))
        eng.workspace['x_data'] = matlab.double(self.data_x.tolist())
        eng.workspace['y_data'] = matlab.double(self.data_y.tolist())
        
        def wrapper(x, y, *p):
            #with open('tmp.log', 'a') as f:
            #    f.write(f'p: {p}\nx: {x}\ny: {np.array(y)}\n\n')
            result = self.cost_func.eval_r(p,
                                           x=np.array(x),
                                           y=np.array(y))
            return result

        # serialize cost_func.eval_cost and open within matlab engine
        # so that matlab fitting function can be called
        eng.workspace['eval_cost_mat'] =\
            self.py_to_mat(wrapper, eng)

        params = self.problem.param_names
        eng.workspace['init_params'] = self.initial_params_mat
        eng.evalc("opts = fitoptions('StartPoint', init_params,"
                  "'Method', 'NonLinearLeastSquares',"
                  f"'Algorithm', '{self.minimizer}')")
        eng.evalc(f"ft = fittype(@({', '.join(params)}, x, y)double(eval_cost_mat(x, y, {', '.join(params)}))', 'options', opts, 'independent', {{'x', 'y'}}, 'dependent', 'z')")


    def fit(self):
        """
        Run problem with Matlab
        """
        eng.evalc("[fitobj, gof, output] = fit([x_data', y_data'], zeros(size(x_data))', ft)")

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        status = int(eng.workspace['output']['exitflag'])
        if status == 1:
            self.flag = 0
        elif status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = eng.coeffvalues(eng.workspace['fitobj'])[0]
        print(self.final_params)
