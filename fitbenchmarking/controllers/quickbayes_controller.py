"""
Implements a controller for the scipy fitting software.
In particular, here for the scipy minimize solver for general minimization
problems.
"""

from quickBayes.fitting.scipy_engine import ScipyFitEngine
from quickBayes.fitting.bumps_engine import Bumps as BumpsFitEngine
#from quickBayes.fitting.bumps_engine import BumpsFitEngine
from fitbenchmarking.controllers.base_controller import Controller
#from fitbenchmarking.controllers.bumpy import BumpsFitEngine

import numpy as np

class quickBayesController(Controller):
    """
    Controller for the Scipy fitting software.
    """

    algorithm_check = {
            'all': ['scipy',
                    'bumps',
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

        self._param_names = [name.replace('.', '_').replace(':', '_').replace('.', '_') for name in self.problem.param_names]

    def setup(self):
        """
        Setup problem ready to be run with SciPy
        """
        p = self.cost_func.problem.function
        if self.minimizer == "scipy":
            lower, upper = p.get_bounds()
            guess = p.get_guess()
            #lower = [-np.inf for _ in range(len(guess))]
            #upper = [np.inf for _ in range(len(guess))]
            self._engine = ScipyFitEngine(self.problem.data_x,
                                          self.problem.data_y,
                                          self.problem.data_e,
                                          lower=lower,
                                          upper=upper,
                                          guess=guess)       
        else:
            self._engine = BumpsFitEngine(self.cost_func.problem.function, self.data_x, self.data_y, self.data_e)
            self._engine.set_function(self.cost_func.problem.function, self._param_names)
        

            # Determine the order of the parameters in `self.fit_problem` as this
            # could differ from the ordering of parameters in `self._param_names`
            self.fit_order = self._engine.fit_order


    def fit(self):
        """
        Run problem with Scipy.
        """
        self.result = self._engine._do_fit(self.problem.data_x,
                                           self.problem.data_y,
                                           self.problem.data_e,
                                           self.cost_func.problem.function)
        #self.result, _ = self._engine.get_fit_parameters()


    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        max_iters_messages = ['maximum number of iterations',
                              'iteration limit reached',
                              'iterations reached limit']

        self.flag = 0
        if self.minimizer == 'scipy':
            self.final_params = self.result
            return
        # Set result variable where parameters are in the same
        # order that are listed in `self._param_names`
        result = []
        if self.fit_order != self._param_names:
            for name in self._param_names:
                ind = self.fit_order.index(name)
                result.append(self.result[ind])
        else:
            result = self.result
        
        self.final_params = result
