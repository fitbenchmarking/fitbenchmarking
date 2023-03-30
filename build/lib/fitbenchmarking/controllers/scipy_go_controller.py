"""
Implements a controller for the scipy fitting software.
In particular, here for the scipy minimize solver for general minimization
problems.
"""

import numpy as np
from scipy import optimize

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError


class ScipyGOController(Controller):
    """
    Controller for the Scipy fitting software.
    """
    controller_name = 'scipy_go'

    algorithm_check = {
        'all': ['differential_evolution', 'shgo', 'dual_annealing'],
        'ls': [None],
        'deriv_free': ['differential_evolution'],
        'general': ['differential_evolution', 'shgo', 'dual_annealing'],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': [],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': ['differential_evolution', 'shgo',
                                'dual_annealing']
    }

    jacobian_enabled_solvers = ['shgo', 'dual_annealing']

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self._popt = None
        self._status = None
        self._maxiter = None

    def setup(self):
        """
        Setup problem ready to be run with SciPy GO
        """
        if self.minimizer == "shgo":
            self._maxiter = 100
        else:
            self._maxiter = 1000
        if self.value_ranges is None or np.any(np.isinf(self.value_ranges)):
            raise MissingBoundsError(
                "SciPy GO requires finite bounds on all parameters")

    def fit(self):
        """
        Run problem with Scipy GO.
        """
        if self.minimizer == "differential_evolution":
            kwargs = {"maxiter": self._maxiter}
        elif self.minimizer == "shgo":
            kwargs = {"options": {"maxiter": self._maxiter,
                                  "jac": self.cost_func.jac_cost}}
        elif self.minimizer == "dual_annealing":
            kwargs = {"maxiter": self._maxiter, "local_search_options": {
                      "jac": self.cost_func.jac_cost}}
        fun = self.cost_func.eval_cost
        bounds = self.value_ranges
        algorithm = getattr(optimize, self.minimizer)
        result = algorithm(fun, bounds, **kwargs)
        self._popt = result.x
        if result.success:
            self._status = 0
        elif "Maximum number of iteration" in result.message:
            self._status = 1
        else:
            self._status = 2

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 1:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._popt
