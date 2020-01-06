"""
Implements a controller for the scipy fitting software.
"""

from scipy.optimize import least_squares

from fitbenchmarking.fitting.controllers.base_controller import Controller


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
        result = least_squares(fun=self.problem.eval_r,
                               x0=self.initial_params,
                               method=self.minimizer,
                               max_nfev=500)

        # To be consistent with Mantid results, we only report when the fit
        # fails. That is when the algorithm diverges or falls over but not
        # when the maximum number of iterations is reached (results.status = 0)
        self.success = (result.status >= 0)
        self._popt = result.x

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(params=self._popt)
            self.final_params = self._popt
