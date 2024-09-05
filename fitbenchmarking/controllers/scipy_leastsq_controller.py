"""
Implements a controller for the scipy fitting software.
In particular, for the scipy leastsq solver.
"""

from scipy.optimize import leastsq

from fitbenchmarking.controllers.base_controller import Controller


class ScipyLeastSqController(Controller):
    """
    Controller for the Scipy leastsq fitting software.
    """

    controller_name = "scipy_leastsq"

    algorithm_check = {
        "all": ["lm-leastsq"],
        "ls": ["lm-leastsq"],
        "deriv_free": [None],
        "general": [None],
        "simplex": [],
        "trust_region": ["lm-leastsq"],
        "levenberg-marquardt": ["lm-leastsq"],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = ["lm-leastsq"]

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = False
        self.param_ranges = None
        self.result = None
        self._status = None
        self._popt = None

    def setup(self):
        """
        Setup problem ready to be run with scipy leastsq
        """
        self.kwargs = {
            "func": self.cost_func.eval_r,
            "x0": self.initial_params,
            "full_output": True,
            "maxfev": 500,
        }
        if not self.cost_func.jacobian.use_default_jac:
            self.kwargs["Dfun"] = self.cost_func.jac_res

    def fit(self):
        """
        Run problem with scipy leastsq.
        """
        self.result = leastsq(**self.kwargs)
        self._popt = self.result[0]
        self._status = self.result[4]

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status in [1, 2, 3, 4]:
            self.flag = 0
        else:
            self.flag = 2

        self.final_params = self._popt
