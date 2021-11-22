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

    algorithm_check = {
            'all': ['Nelder-Mead', 'Powell', 'CG', 'BFGS', 'Newton-CG',
                    'L-BFGS-B', 'TNC', 'SLSQP'],
            'ls': [None],
            'deriv_free': ['Nelder-Mead', 'Powell'],
            'general': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                        'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP'],
            'simplex': ['Nelder-Mead'],
            'trust_region': [],
            'levenberg-marquardt': [],
            'gauss_newton': [],
            'bfgs': ['BFGS', 'L-BFGS-B'],
            'conjugate_gradient': ['CG', 'Newton-CG', 'Powell'],
            'steepest_descent': [],
            'global_optimization': []}

    jacobian_enabled_solvers = ['CG', 'BFGS', 'Newton-CG',
                                'L-BFGS-B', 'TNC', 'SLSQP']

    hessian_enabled_solvers = ['Newton-CG']

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
        self._popt = None

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
        if self.minimizer in self.jacobian_enabled_solvers:
            if not self.cost_func.jacobian.use_default_jac:
                kwargs["jac"] = self.cost_func.jac_cost
            elif self.cost_func.jacobian.use_default_jac and self.minimizer == "Newton-CG":
                jac = self._create_default_jacobian_for_newton_cg()
                kwargs["jac"] = jac.eval
        if self.minimizer not in self.no_bounds_minimizers:
            kwargs["bounds"] = self.value_ranges
        if self.cost_func.hessian and \
                self.minimizer in self.hessian_enabled_solvers:
            kwargs["hess"] = self.cost_func.hes_cost
        self.result = minimize(**kwargs)
        self._popt = self.result.x

    def _create_default_jacobian_for_newton_cg(self):
        """
        Creates a default Jacobian to use for the Newton-CG minimizer in
        Scipy. Unfortunately, the Newton-CG minimizer has a different
        interface than the other minimizers in Scipy which requires a
        callable Jacobian to be passed at all times. This function should
        be removed when the Newton-CG minimizer is harmonized with the other
        Scipy minimizers.
        """
        from fitbenchmarking.jacobian.scipy_jacobian import Scipy
        jac = Scipy(self.cost_func.problem)
        jac.method = "2-point"
        return jac

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        max_iters_messages = ['maximum number of iterations',
                              'iteration limit reached',
                              'iterations reached limit']

        if self.result.success:
            self.flag = 0
        elif any(message in self.result.message.lower()
                 for message in max_iters_messages):
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._popt
