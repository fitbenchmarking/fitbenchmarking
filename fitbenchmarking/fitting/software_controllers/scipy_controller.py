
import numpy as np
from scipy.optimize import curve_fit

from fitbenchmarking.fitting.software_controllers.base_software_controller import \
    BaseSoftwareController


class ScipyController(BaseSoftwareController):
    """
    Controller for the Scipy fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Initialises variable used for temporary storage.
        """
        super(ScipyController, self).__init__(problem, use_errors)

        self.popt = None

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

        popt, _ = curve_fit(f=self.function.__call__,
                            xdata=self.data_x,
                            ydata=self.data_y,
                            p0=self.initial_params,
                            sigma=self.data_e,
                            method=self.minimizer,
                            maxfev=500)

        self.success = (popt is not None)
        self.popt = popt

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.function(self.data_x, *self.popt)
            self.final_params = self.popt
