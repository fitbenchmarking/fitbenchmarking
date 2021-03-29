"""
Implements a controller for RALFit
https://github.com/ralna/RALFit
"""

import ral_nlls
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class RALFitController(Controller):
    """
    Controller for the RALFit fitting software.
    """

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super(RALFitController, self).__init__(cost_func)

        self.support_for_bounds = True
        self._param_names = self.problem.param_names
        self._popt = None
        self._options = {}
        self.algorithm_check = {
            'all': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'ls': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'deriv_free': [None],
            'general': [None]}

    def jacobian_information(self):
        """
        RALFit can use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

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

        value_ranges_lb = []
        value_ranges_ub = []
        for name in self._param_names:
            if self.problem.value_ranges is not None \
                    and name in self.problem.value_ranges:
                value_ranges_lb.extend([self.problem.value_ranges[name][0]])
                value_ranges_ub.extend([self.problem.value_ranges[name][1]])
            else:
                value_ranges_lb.extend([-np.inf])
                value_ranges_ub.extend([np.inf])
        self.value_ranges = (value_ranges_lb, value_ranges_ub)

    def fit(self):
        """
        Run problem with RALFit.
        """
        self._popt = ral_nlls.solve(self.initial_params,
                                    self.cost_func.eval_r,
                                    self.jacobian.eval,
                                    options=self._options,
                                    lower_bounds=self.value_ranges[0],
                                    upper_bounds=self.value_ranges[1])[0]
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
