"""
Implements a controller for the scipy ls fitting software.
In particular, for the scipy least_squares solver.
"""

import numpy as np
from scipy.optimize import least_squares

from fitbenchmarking.controllers.base_controller import Controller


class ScipyLSController(Controller):
    """
    Controller for the Scipy Least-Squares fitting software.
    """

    controller_name = "scipy_ls"

    algorithm_check = {
        "all": ["lm-scipy", "trf", "dogbox"],
        "ls": ["lm-scipy", "trf", "dogbox"],
        "deriv_free": [None],
        "general": [None],
        "simplex": [],
        "trust_region": ["lm-scipy", "trf", "dogbox"],
        "levenberg-marquardt": ["lm-scipy"],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = ["lm-scipy", "trf", "dogbox"]

    sparsity_enabled_solvers = ["trf", "dogbox"]

    no_bounds_minimizers = ["lm-scipy"]
    support_for_bounds = True

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.param_ranges = None
        self.result = None
        self._status = None
        self._popt = None
        # Need to map the minimizer to an internal one to avoid changing the
        # minimizer in results
        self._minimizer = ""

    def setup(self):
        """
        Setup problem ready to be run with SciPy LS
        """

        if self.minimizer == "lm-scipy":
            self._minimizer = "lm"
        else:
            self._minimizer = self.minimizer

        # If parameter ranges have been set in problem, then set up bounds
        # option for scipy least_squares function. Here the bounds option
        # must be a 2 tuple array like object, the first tuple containing
        # the lower bounds for each parameter and the second containing all
        # upper bounds.
        if self.value_ranges is not None:
            value_ranges_lb, value_ranges_ub = zip(*self.value_ranges)
            self.param_ranges = (list(value_ranges_lb), list(value_ranges_ub))
        else:
            self.param_ranges = (
                [-np.inf] * len(self.initial_params),
                [np.inf] * len(self.initial_params),
            )

    def fit(self):
        """
        Run problem with Scipy LS.
        """
        kwargs = {
            "fun": self.cost_func.eval_r,
            "x0": self.initial_params,
            "method": self._minimizer,
            "max_nfev": 500,
        }
        if not self.cost_func.jacobian.use_default_jac:
            kwargs["jac"] = self.cost_func.jac_res
        if self.minimizer != "lm":
            kwargs["bounds"] = self.param_ranges
        self.result = least_squares(**kwargs)
        self._popt = self.result.x
        self._status = self.result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status > 0:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.func_evals = self.result.nfev
        self.final_params = self._popt
