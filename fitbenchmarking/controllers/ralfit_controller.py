"""
Implements a controller for RALFit
https://github.com/ralna/RALFit
"""

import ral_nlls

from fitbenchmarking.controllers.base_controller import Controller


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

        # Use bytestrings explicitly as thats whats expected in RALFit and
        # python 3 defaults to unicode.
        self._options[b"maxit"] = 500
        if self.minimizer == "gn":
            self._options[b"model"] = 1
            self._options[b"nlls_method"] = 4
        elif self.minimizer == "gn_reg":
            self._options[b"model"] = 1
            self._options[b"type_of_method"] = 2
        elif self.minimizer == "hybrid":
            self._options[b"model"] = 3
            self._options[b"nlls_method"] = 4
        elif self.minimizer == "hybrid_reg":
            self._options[b"model"] = 3
            self._options[b"type_of_method"] = 2
        else:
            raise RuntimeError("An undefined RALFit minmizer was selected")

    def fit(self):
        """
        Run problem with RALFit.
        """
        self.success = False
        self._popt = ral_nlls.solve(self.initial_params,
                                    self.problem.eval_r,
                                    self.problem.eval_j,
                                    options=self._options)[0]
        self.success = (self._popt is not None)
        self._status = 0 if self.success else 1

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
        else:
            self.flag = 2
