
import numpy as np
from scipy.optimize import curve_fit

from fitbenchmarking.fitting.software_controllers.base_software_controller import \
    BaseSoftwareController


class ScipyController(BaseSoftwareController):

    def __init__(self, problem, use_errors):
        super(ScipyController, self).__init__(problem, use_errors)

        self.popt = None

        xdata = problem.data_x
        ydata = problem.data_y

        # fix sigma
        sigma = None
        if use_errors:
            sigma = problem.data_e

            if sigma is None:
                sigma = np.sqrt(abs(ydata))

            sigma[sigma == 0] = 1e-8

        # impose x ranges
        start_x = problem.start_x
        end_x = problem.end_x

        if start_x is not None and end_x is not None:
            mask = np.logical_and(xdata > start_x, xdata < end_x)
            xdata = xdata[mask]
            ydata = ydata[mask]
            if sigma is not None:
                sigma = sigma[mask]

        # store
        self.data_x = xdata
        self.data_y = ydata
        self.data_e = sigma

    def setup(self):
        """
        Setup specifics for problem ready to run with Scipy.

        :returns: None
        :rtype: None
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
        Convert the result to a numpy array and store it.
        """
        self.results = self.function(self.data_x, *self.popt)
        self.final_params = self.popt
