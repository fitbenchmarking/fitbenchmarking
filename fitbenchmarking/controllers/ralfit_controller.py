"""
Implements a controller for RALFit
https://github.com/ralna/RALFit
"""

import ral_nlls

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class RALFitController(Controller):
    """
    Controller for the RALFit fitting software.
    """

    def __init__(self, problem):
        """
        Initialises variable used for temporary storage.

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(RALFitController, self).__init__(problem)

        self._popt = None
        self._options = {}
        self.algorithm_check = {
            'all': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'ls': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'deriv_free': [None],
            'general': [None]}

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
            raise UnknownMinimizerError(
                "No {} minimizer for RALFit".format(self.minimizer))

    def fit(self):
        """
        Run problem with RALFit.
        """
        self._popt = ral_nlls.solve(self.initial_params,
                                    self.problem.eval_r,
                                    self.problem.jac.eval,
                                    options=self._options)[0]
        self._status = 0 if self._popt is not None else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        else:
            self.flag = 2

        self.final_params = self._popt
