"""
Implements a controller for global optimization algorithms.
"""
import numpy as np

from gofit import alternating, multistart, regularisation

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError, UnknownMinimizerError


class GOFitController(Controller):
    """
    Controller for GOFit multistart global optimisation algorithms
    """

    algorithm_check = {
        'all': ['alternating', 'multistart', 'regularisation'],
        'ls': ['alternating', 'multistart', 'regularisation'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': ['regularisation'],
        'gauss_newton': ['regularisation'],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': ['alternating', 'multistart']
    }

    jacobian_enabled_solvers = ['multistart', 'regularisation']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)
        self.support_for_bounds = True
        self.no_bounds_minimizers = ['regularisation']
        self.options = None
        self._popt = None

    def setup(self):
        """
        Setup problem ready to be run with GoFit
        """

        # these are the GOFit defaults (for now)
        self.options = {'maxit': 200,
                        'samples': 100,
                        'eps_r': 1e-5,
                        'eps_g': 1e-4,
                        'eps_s': 1e-8
                        }

        if self.value_ranges is None:
            raise MissingBoundsError("GOFit requires bounds on parameters")

        low, high = zip(*self.value_ranges)
        self._low = np.array(low)
        self._high = np.array(high)
        self._x0 = self.initial_params  # store initial guess params

    def fit(self):
        """
        Run problem with GoFit
        """
        # initial paramter guess
        x0 = self._x0

        # lower and upper bounds of the parameters to optimize
        xl = self._low
        xu = self._high

        # number of dimensions of problem
        n = len(self._low)
        m = len(self.data_x)

        # split point for alternating optimization
        n_split = 9  # All B parameters

        # Optimization based on minimizer selected
        if self.minimizer == "alternating":
            xopt, status = alternating(
                m, n, n_split, x0, xl, xu, self.cost_func.eval_r, **self.options)
        elif self.minimizer == "multistart":
            if not self.cost_func.jacobian.use_default_jac:
                self.options['jac'] = self.cost_func.jac_res
            xopt, status = multistart(
                m, n, xl, xu, self.cost_func.eval_r, **self.options)
        elif self.minimizer == "regularisation":
            del self.options['eps_r']
            del self.options['samples']
            if not self.cost_func.jacobian.use_default_jac:
                self.options['jac'] = self.cost_func.jac_res
            xopt, status = regularisation(
                m, n, x0, self.cost_func.eval_r, **self.options)
        else:
            raise UnknownMinimizerError(
                "No {} minimizer for GOFit".format(self.minimizer))

        self._popt = xopt
        self._status = status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        if self._status == 0:
            self.flag = 0
        elif self._status == 1:
            self.flag = 1
        else:
            self.flag = 3

        self.final_params = self._popt
