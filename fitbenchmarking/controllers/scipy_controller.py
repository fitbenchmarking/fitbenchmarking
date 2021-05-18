"""
Implements a controller for the scipy fitting software.
In particular, here for the scipy minimize solver for general minimization
problems.
"""

from scipy.optimize import minimize

from fitbenchmarking.controllers.base_controller import Controller


class ScipyController(Controller):
    """
    Controller for the Scipy fitting software.
    """

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.no_bounds_minimizers = ['Nelder-Mead', 'CG', 'BFGS', 'Newton-CG']
        self.options = None
        self.result = None
        self._status = None
        self._popt = None
        self.algorithm_check = {
            'all': ['Nelder-Mead', 'Powell', 'CG', 'BFGS', 'Newton-CG',
                    'L-BFGS-B', 'TNC', 'SLSQP'],
            'ls': [None],
            'deriv_free': ['Nelder-Mead', 'Powell'],
            'general': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                        'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP']}

    def jacobian_information(self):
        """
        Scipy can use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = ["Nelder-Mead", "Powell"]
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup problem ready to be run with SciPy
        """
        self.options = {'maxiter': 500}

    def fit(self):
        """
        Run problem with Scipy.
        """
        kwargs = {"fun": self.cost_func.eval_cost,
                  "x0": self.initial_params,
                  "method": self.minimizer,
                  "options": self.options}
        if self.minimizer not in ["Nelder-Mead", "Powell"]:
            # Neither the Nelder-Mead or Powell minimizers require a Jacobian
            # so are run without that argument.
            if not self.jacobian.use_default_jac:
                kwargs["jac"] = self.jacobian.eval_cost
        if self.minimizer not in self.no_bounds_minimizers:
            kwargs["bounds"] = self.value_ranges
        self.result = minimize(**kwargs)
        self._popt = self.result.x
        self._status = self.result.status

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

        self.final_params = self._popt
