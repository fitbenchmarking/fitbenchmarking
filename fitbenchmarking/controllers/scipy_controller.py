"""
Implements a controller for the scipy fitting software.
"""

from scipy.optimize import least_squares

from fitbenchmarking.controllers.base_controller import Controller


class ScipyController(Controller):
    """
    Controller for the Scipy fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Initialises variable used for temporary storage.
        """
        super(ScipyController, self).__init__(problem, use_errors)

        self._popt = None

    def setup(self):
        """
        No setup needed for scipy, so this is a no-op.
        """
        if self.minimizer == "lm-scipy":
            self.minimizer = "lm"

    def fit(self):
        """
        Run problem with Scipy.
        """
        self.result = least_squares(fun=self.problem.eval_r,
                                    x0=self.initial_params,
                                    method=self.minimizer,
                                    max_nfev=500)
        self.success = (self.result.status >= 0)
        self._popt = self.result.x
        self._status = self.result.status

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
        if self._status > 0:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2
        self.error_message = self.error_options[self.flag]
