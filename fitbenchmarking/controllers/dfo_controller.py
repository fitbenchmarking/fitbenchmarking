"""
Implements a controller for DFO-GN
http://people.maths.ox.ac.uk/robertsl/dfogn/
"""

import dfogn
import dfols
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class DFOController(Controller):
    """
    Controller for the DFO-{GN/LS} fitting software.
    """

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super(DFOController, self).__init__(cost_func)

        self.support_for_bounds = True
        self._soln = None
        self._popt = None
        self._pinit = None
        self.algorithm_check = {
            'all': ['dfogn', 'dfols'],
            'ls': ['dfogn', 'dfols'],
            'deriv_free': ['dfogn', 'dfols'],
            'general': [None]}

    def jacobian_information(self):
        """
        DFO cannot use Jacobian information
        """
        has_jacobian = False
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for DFO
        """
        self._pinit = np.asarray(self.initial_params)

        value_ranges_lb = np.array([])
        value_ranges_ub = np.array([])
        bound_range = np.array([])
        for name in self._param_names:
            if self.problem.value_ranges is not None \
                    and name in self.problem.value_ranges:
                value_ranges_lb = np.append(value_ranges_lb,
                                            self.problem.value_ranges[name][0])
                value_ranges_ub = np.append(value_ranges_ub,
                                            self.problem.value_ranges[name][1])
                bound_range = np.append(bound_range,
                                        self.problem.value_ranges[name][1]
                                        - self.problem.value_ranges[name][0])
            else:
                value_ranges_lb = np.append(value_ranges_lb, -10e+20)
                value_ranges_ub = np.append(value_ranges_ub, 10e+20)
        self.value_ranges = (value_ranges_lb, value_ranges_ub)

        # if bounds are set then gap between lower and upper bound must
        # be at least 2*rhobeg so check that default rhobeg value
        # satisfies this condition
        self.rhobeg = 0.1*max(np.linalg.norm(self._pinit, np.inf), 1)
        if bound_range.size:
            if min(bound_range) <= 2*self.rhobeg:
                self.rhobeg = min(bound_range/2)

    def fit(self):
        """
        Run problem with DFO.
        """
        if self.minimizer == 'dfogn':
            self._soln = dfogn.solve(self.cost_func.eval_r,
                                     self._pinit,
                                     rhobeg=self.rhobeg,
                                     lower=self.value_ranges[0],
                                     upper=self.value_ranges[1])
        elif self.minimizer == 'dfols':
            self._soln = dfols.solve(self.cost_func.eval_r,
                                     self._pinit,
                                     rhobeg=self.rhobeg,
                                     bounds=(self.value_ranges))

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
