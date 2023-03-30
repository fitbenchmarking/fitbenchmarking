"""
Implements a controller for global optimization algorithms.
"""
import numpy as np

from gofit import alternating, multistart, regularisation

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError
from fitbenchmarking.utils.exceptions import UnknownMinimizerError
from fitbenchmarking.utils.exceptions import IncompatibleMinimizerError


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
        self._options = None
        self._nsplit = None
        self._p0 = None
        self._pl = None
        self._pu = None
        self._status = None
        self._popt = None

    def setup(self):
        """
        Setup problem ready to be run with GoFit
        """

        # these are the GOFit defaults (for now)
        self._options = {'maxit': 200,
                         'samples': 100,
                         'eps_r': 1e-5,
                         'eps_g': 1e-4,
                         'eps_s': 1e-8
                         }

        if self.value_ranges is None and self.minimizer != "regularisation":
            raise MissingBoundsError(
                "GOFit global minimizers require bounds on parameters")

        # set split point for CrystalField problems
        if self.minimizer == "alternating":
            try:
                self._nsplit = self.problem.param_names.index(
                    'IntensityScaling')
            except ValueError as minimizer_incompatible:
                raise IncompatibleMinimizerError(
                    "alternating minimizer currently only supports "
                    "CrystalField problems") from minimizer_incompatible

        if self.minimizer != "regularisation":
            low, high = zip(*self.value_ranges)
            self._pl = np.array(low)
            self._pu = np.array(high)

        self._p0 = self.initial_params  # store initial guess params

    def fit(self):
        """
        Run problem with GoFit
        """

        # number of dimensions of problem
        n = len(self._p0)
        m = len(self.data_x)

        # Optimization based on minimizer selected
        if self.minimizer == "alternating":
            xopt, status = alternating(
                m, n, self._nsplit, self._p0, self._pl, self._pu,
                self.cost_func.eval_r, **self._options)
        elif self.minimizer == "multistart":
            if not self.cost_func.jacobian.use_default_jac:
                self._options['jac'] = self.cost_func.jac_res
            xopt, status = multistart(
                m, n, self._pl, self._pu, self.cost_func.eval_r,
                **self._options)
        elif self.minimizer == "regularisation":
            del self._options['eps_r']
            del self._options['samples']
            if not self.cost_func.jacobian.use_default_jac:
                self._options['jac'] = self.cost_func.jac_res
            xopt, status = regularisation(
                m, n, self._p0, self.cost_func.eval_r, **self._options)
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
