"""
Implements a controller for DFO-LS
https://numericalalgorithmsgroup.github.io/dfols/build/html/index.html
"""

import dfols
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class DFOController(Controller):
    """
    Controller for the DFO-LS fitting software.
    """

    algorithm_check = {
            'all': ['dfols'],
            'ls': ['dfols'],
            'deriv_free': ['dfols'],
            'general': [],
            'simplex': [],
            'trust_region': ['dfols'],
            'levenberg-marquardt': [],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': [],
            'MCMC': []}

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.param_ranges = None
        self.rhobeg = None
        self._status = None
        self._soln = None
        self._popt = None
        self._pinit = None

    def setup(self):
        """
        Setup for DFO
        """
        self._pinit = np.asarray(self.initial_params)

        # set parameter ranges
        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            lb = [-10e+20 if x == -np.inf else x for x in lb]
            ub = [10e+20 if x == np.inf else x for x in ub]
            self.param_ranges = (np.array(lb), np.array(ub))

            # if bounds are set then gap between lower and upper bound must
            # be at least 2*rhobeg so check that default rhobeg value
            # satisfies this condition
            bound_range = np.array(
                [ub_i - lb_i for lb_i, ub_i in self.value_ranges])
            self.rhobeg = 0.1*max(np.linalg.norm(self._pinit, np.inf), 1)
            if min(bound_range) <= 2*self.rhobeg:
                self.rhobeg = min(bound_range/2)
        else:
            self.param_ranges = (
                np.array([-10e+20]*len(self.initial_params)),
                np.array([10e+20]*len(self.initial_params)))
            self.rhobeg = 0.1*max(np.linalg.norm(self._pinit, np.inf), 1)

    def fit(self):
        """
        Run problem with DFO.
        """
        self._soln = dfols.solve(self.cost_func.eval_r,
                                 self._pinit,
                                 rhobeg=self.rhobeg,
                                 bounds=self.param_ranges)

        self._popt = self._soln.x
        self._status = self._soln.flag

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
