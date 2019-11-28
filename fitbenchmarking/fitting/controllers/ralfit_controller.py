"""
Implements a controller for RALFit
https://github.com/ralna/RALFit
"""

import ral_nlls
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.fitting.controllers.base_controller import Controller


class RALFitController(Controller):
    """
    Controller for the RALFit fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Initialises variable used for temporary storage.
        """
        super(RALFitController, self).__init__(problem, use_errors)

        self._popt = None
        self._options = {}

    def setup(self):
        """
        Setup for RALFit
        """
        self._options["maxit"] = 500
        if self.minimizer == "gn":
            self._options["model"] = 1
            self._options["nlls_method"] = 4
        elif self.minimizer == "gn_reg":
            self._options["model"] = 1
            self._options["type_of_method"] = 2
        elif self.minimizer == "hybrid":
            self._options["model"] = 3
            self._options["nlls_method"] = 4
        elif self.minimizer == "hybrid_reg":
            self._options["model"] = 3
            self._options["type_of_method"] = 2
        else:
            raise RuntimeError("An undefined RALFit minmizer was selected")

    def _prediction_error(self, p):
        f = self.problem.eval_f(x=self.data_x,
                                params=p)
        f = f - self.data_y
        if self.use_errors:
            f = f / self.data_e

        return f

    def _jac(self, p):
        j = approx_derivative(self._prediction_error,
                              p)
        return j

    def fit(self):
        """
        Run problem with RALFit.
        """
        self.success = False
        self._popt = ral_nlls.solve(self.initial_params,
                                    self._prediction_error,
                                    self._jac,
                                    options=self._options)[0]

        self.success = (self._popt is not None)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(x=self.data_x,
                                               params=self._popt)
            self.final_params = self._popt
