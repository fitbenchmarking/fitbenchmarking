"""
Implements a controller for the Bumps fitting software.
"""

from bumps.fitters import fit as bumpsFit
from bumps.names import Curve, FitProblem, PoissonCurve

import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.utils.exceptions import MaxRuntimeError


class BumpsController(Controller):
    """
    Controller for the Bumps fitting software.

    Sasview requires a model to fit.
    Setup creates a model with the correct function.
    """

    algorithm_check = {
            'all': ['amoeba',
                    'lm-bumps',
                    'newton',
                    'de',
                    'scipy-leastsq',
                    'dream'],
            'ls': ['lm-bumps', 'scipy-leastsq'],
            'deriv_free': ['amoeba', 'de', 'dream'],
            'general': ['amoeba', 'newton', 'de', 'dream'],
            'simplex': ['amoeba'],
            'trust_region': ['lm-bumps', 'scipy-leastsq'],
            'levenberg-marquardt': ['lm-bumps', 'scipy-leastsq'],
            'gauss_newton': [],
            'bfgs': ['newton'],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': ['de', 'dream']}

    def __init__(self, cost_func):
        """
        Extract param names for function setup

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self._param_names = [name.replace('.', '_')
                             for name in self.problem.param_names]
        self.support_for_bounds = True
        self._func_wrapper = None
        self._fit_problem = None
        self.fit_order = None
        self._status = None
        self._bumps_result = None
        # Need to map the minimizer to an internal one to avoid changing the
        # minimizer in results
        self._minimizer = ''

    def setup(self):
        # pylint: disable=exec-used,protected-access
        """
        Setup problem ready to run with Bumps.

        Creates a FitProblem for calling in the fit() function of Bumps
        """
        # Bumps fails with the *args notation
        param_name_str = ', '.join(self._param_names)
        wrapper = "def fitFunction(x, {}):\n".format(param_name_str)
        wrapper += "    return func([{}], x=x)".format(param_name_str)

        # Remove any function attribute. BinWidth is the only attribute in all
        # FitBenchmark (Mantid) problems.
        param_dict = dict(zip(self._param_names, self.initial_params))

        # Create a Function Wrapper for the problem function. The type of the
        # Function Wrapper is acceptable by Bumps.
        if isinstance(self.cost_func, create_cost_func('poisson')):
            # Bumps has a built in poisson cost fucntion, so use that.
            exec_dict = {'func': self.problem.eval_model}
            exec(wrapper, exec_dict)
            model = exec_dict['fitFunction']
            func_wrapper = PoissonCurve(fn=model,
                                        x=self.data_x,
                                        y=self.data_y,
                                        **param_dict)
        else:  # nlls cost functions
            # Send in the residual as the model, with zero
            # y data.  This allows all our supported nlls
            # cost fucntions to be used.
            exec_dict = {'func': self.cost_func.eval_r}
            exec(wrapper, exec_dict)
            model = exec_dict['fitFunction']
            zero_y = np.zeros(len(self.data_y))
            func_wrapper = Curve(fn=model,
                                 x=self.data_x,
                                 y=zero_y,
                                 **param_dict)

        # Set a range for each parameter
        for ind, name in enumerate(self._param_names):
            if self.value_ranges is not None:
                min_val = self.value_ranges[ind][0]
                max_val = self.value_ranges[ind][1]
            else:
                min_val = -np.inf
                max_val = np.inf
            func_wrapper.__dict__[name].range(min_val, max_val)

        # Create a Problem Wrapper. The type of the Problem Wrapper is
        # acceptable by Bumps fitting.
        self._func_wrapper = func_wrapper
        self._fit_problem = FitProblem(func_wrapper)

        # Determine the order of the parameters in `self.fit_problem` as this
        # could differ from the ordering of parameters in `self._param_names`
        param_order = []
        for i in range(len(self._param_names)):
            param_order.append(str(self._fit_problem._parameters[i]))
        self.fit_order = param_order

        if self.minimizer == "lm-bumps":
            self._minimizer = "lm"
        elif self.minimizer == "scipy-leastsq":
            self._minimizer = "scipy.leastsq"
        else:
            self._minimizer = self.minimizer

    def _check_timer_abort_test(self):
        """
        Boolean check for if the fit should be stopped.

        :return: If the time limit has been reached.
        :rtype: bool
        """
        try:
            self.timer.check_elapsed_time()
        except MaxRuntimeError:
            return True
        return False

    def fit(self):
        """
        Run problem with Bumps.
        """
        result = bumpsFit(self._fit_problem,
                          method=self._minimizer,
                          abort_test=self._check_timer_abort_test)

        self._bumps_result = result
        self._status = self._bumps_result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 2:
            self.flag = 1
        else:
            self.flag = 2

        # Set result variable where parameters are in the same
        # order that are listed in `self._param_names`
        result = []
        if self.fit_order != self._param_names:
            for name in self._param_names:
                ind = self.fit_order.index(name)
                result.append(self._bumps_result.x[ind])
        else:
            result = self._bumps_result.x

        self.final_params = result
