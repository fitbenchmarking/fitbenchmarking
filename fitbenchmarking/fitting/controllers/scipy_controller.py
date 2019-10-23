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
        pass

    def fit(self):
        """
        Run problem with Scipy.
        """
        popt = None

        popt, _ = curve_fit(f=self.functions[self.function_id][0].__call__,
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
            self.results = self.problem.eval_f(x=self.data_x,
                                               params=self._popt,
                                               function_id=self.function_id)
            self.final_params = self._popt
