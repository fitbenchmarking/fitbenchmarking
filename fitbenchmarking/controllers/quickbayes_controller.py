"""
Implements a controller for the scipy fitting software.
In particular, here for the scipy minimize solver for general minimization
problems.
"""

from quickBayes.fitting.scipy_engine import ScipyFitEngine
from fitbenchmarking.controllers.base_controller import Controller


class quickBayesController(Controller):
    """
    Controller for the Scipy fitting software.
    """

    algorithm_check = {
            'all': ['scipy',
                    ],
            'ls': [None],
            'deriv_free': [],
            'general': [],
            'simplex': [],
            'trust_region': [],
            'levenberg-marquardt': [],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': [],
            'MCMC': []}

    jacobian_enabled_solvers = []
    hessian_enabled_solvers = []

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.options = None
        self.result = None
        self._popt = None

    def setup(self):
        """
        Setup problem ready to be run with SciPy
        """
        p = self.cost_func.problem.function
        lower, upper = p.get_bounds()
        guess = p.get_guess()
        self._engine = ScipyFitEngine(self.problem.data_x,
                                      self.problem.data_y,
                                      self.problem.data_e,
                                      lower=lower,
                                      upper=upper,
                                      guess=guess)       
    
    def fit(self):
        """
        Run problem with Scipy.
        """
        self._engine.do_fit(self.problem.data_x,
                            self.problem.data_y,
                            self.problem.data_e,
                            self.cost_func.problem.function)
        #self.result = minimize(**kwargs)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        max_iters_messages = ['maximum number of iterations',
                              'iteration limit reached',
                              'iterations reached limit']

        self.flag = 0

        self.final_params, _ = self._engine.get_fit_parameters()
