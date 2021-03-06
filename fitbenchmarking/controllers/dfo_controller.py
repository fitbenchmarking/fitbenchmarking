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

    def fit(self):
        """
        Run problem with DFO.
        """
        if self.minimizer == 'dfogn':
            self._soln = dfogn.solve(self.cost_func.eval_r,
                                     self._pinit)
        elif self.minimizer == 'dfols':
            self._soln = dfols.solve(self.cost_func.eval_r,
                                     self._pinit)

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
