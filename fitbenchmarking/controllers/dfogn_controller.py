"""
Implements a controller for DFO-GN
http://people.maths.ox.ac.uk/robertsl/dfogn/
"""

import dfogn
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


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

    def fit(self):
        """
        Run problem with DFO-GN.
        """
        self.success = False

        self._soln = dfogn.solve(self.problem.eval_r,
                                 self._pinit)

        if (self._soln.flag == 0):
            self.success = True

        self._popt = self._soln.x
        self._status = self._soln.flag

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(params=self._popt)
            self.final_params = self._popt

    def error_flags(self):
        """
        Sets the error flags for the controller, the options are:
            {0: "Successfully converged",
             1: "Software reported maximum number of iterations exceeded",
             2: "Software run but didn't converge to solution",
             3: "Software raised an exception"}
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 2:
            self.flag = 1
        else:
            self.flag = 2
