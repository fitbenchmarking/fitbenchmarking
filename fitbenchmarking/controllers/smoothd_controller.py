"""
Implements a controller for the SmoothD global optimization algorithm.
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative
import sys
sys.path.append("/home/upg88743/global-optimization/")
from SmoothD.smoothd import smoothd
from SmoothD.smoothd_improved import smoothd_improved
from SmoothD.rembed import rembed

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError, UnknownMinimizerError

class SmoothdController(Controller):
    """
    Controller for the SmoothD global optimization algorithm.
    """

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super(SmoothdController, self).__init__(cost_func)

        self.support_for_bounds = True
        self._popt = None
        self._demb = None
        self.algorithm_check = {
            'all': ['SmoothD', 'SmoothD-Improved', 'Rembed'],
            'ls': [None],
            'deriv_free': [None],
            'general': ['SmoothD', 'SmoothD-Improved', 'Rembed'],
            'global_optimization': ['SmoothD', 'SmoothD-Improved', 'Rembed']
        }

    jacobian_enabled_solvers = ['SmoothD', 'SmoothD-Improved', 'Rembed']

    def setup(self):
        """
        Setup problem ready to be run with SmoothD
        """
        self._options = {'maxit': 1000, 'eps': 1e-5, 'rbar': 2.8, 'C': 50}
        if self.minimizer == "SmoothD-Improved":
            self._options['prune'] = True
            self._options['lsearch'] = True
        if self.minimizer == "Rembed":
            self._options['maxemb'] = 100
            self._demb = 2
        #self._options['plot'] = True

        # Set bounds on parameters
        if self.value_ranges is None:
            raise MissingBoundsError("SmoothD requires bounds on parameters")
        xl, xu = zip(*self.value_ranges)
        self._xl = np.array(xl)
        self._xu = np.array(xu)

    def fit(self):
        """
        Run problem with SmoothD.
        """
        xl = self._xl
        xu = self._xu
        def f(y): return self.cost_func.eval_cost(xl + (xu-xl)*y)
        def g(y): return approx_derivative(f, y, method=self.jacobian.method)
        yl = np.zeros_like(xl)
        yu = np.ones_like(xu)
        d = self._demb
        if self.minimizer == "SmoothD-Improved":
            status, _, yopt = smoothd_improved(f, g, yl, yu, **self._options)
        elif self.minimizer == "SmoothD":
            status, _, yopt = smoothd(f, g, yl, yu, **self._options)
        elif self.minimizer == "Rembed":
            status, _, yopt = rembed(f, g, yl, yu, d, **self._options)
        else:
            raise UnknownMinimizerError(self.minimizer+" minimizer does not exist")
        self._popt = xl + (xu-xl)*yopt
        self._status = status

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
            self.flag = 3

        self.final_params = self._popt
