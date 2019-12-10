"""
Implements a controller for the scipy fitting software.
"""

from scipy.optimize import curve_fit

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
        popt = None

        # Use self.problem.function here instead of eval_f as the arguments
        # need to be passed separately
        popt, _ = curve_fit(f=self.problem.function,
                            xdata=self.data_x,
                            ydata=self.data_y,
                            p0=self.initial_params,
                            sigma=self.data_e,
                            method=self.minimizer,
                            maxfev=500)

        self.success = (popt is not None)
        self._popt = popt

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(params=self._popt)
            self.final_params = self._popt
