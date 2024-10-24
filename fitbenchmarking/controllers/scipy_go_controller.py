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
                                'dual_annealing'],
        'MCMC': []
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
        self._result = None
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
        if self.minimizer == "shgo":
            kwargs = {"options": {"maxiter": self._maxiter,
                                  "jac": self.cost_func.jac_cost}}
        elif self.minimizer == "dual_annealing":
            kwargs = {
                "maxiter": self._maxiter,
                "minimizer_kwargs": {"jac": self.cost_func.jac_cost},
            }
        else:  # differential_evolution
            kwargs = {"maxiter": self._maxiter}
        fun = self.cost_func.eval_cost
        bounds = self.value_ranges
        algorithm = getattr(optimize, self.minimizer)
        self._result = algorithm(fun, bounds, **kwargs)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._result.success:
            self.flag = 0
        elif "Maximum number of iteration" in self._result.message:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._result.x
        self.iteration_count = self._result.nit
        self.func_evals = self._result.nfev
