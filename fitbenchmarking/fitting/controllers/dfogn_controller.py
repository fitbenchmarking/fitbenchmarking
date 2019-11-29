"""
Implements a controller for DFO-GN
http://people.maths.ox.ac.uk/robertsl/dfogn/
"""

import dfogn
import numpy as np

from fitbenchmarking.fitting.controllers.base_controller import Controller


class DFOGNController(Controller):
    """
    Controller for the DFO-GN fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Initialises variable used for temporary storage.
        """
        super(DFOGNController, self).__init__(problem, use_errors)

        self._soln = None
        self._popt = None
        self._pinit = None

    def setup(self):
        """
        Setup for DFO-GN
        """
        self._pinit = np.asarray(self.initial_params)

    def _prediction_error(self, p):
        f = self.data_y - self.problem.eval_f(params=p)
        if self.use_errors:
            f = f/self.data_e

        return f

    def fit(self):
        """
        Run problem with DFO-GN.
        """
        self.success = False

        self._soln = dfogn.solve(self._prediction_error,
                                 self._pinit)

        if (self._soln.flag == 0):
            self.success = True

        self._popt = self._soln.x

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(params=self._popt)
            self.final_params = self._popt
