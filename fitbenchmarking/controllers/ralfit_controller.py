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

    algorithm_check = {
            'all': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'ls': ['gn', 'hybrid', 'gn_reg', 'hybrid_reg'],
            'deriv_free': [],
            'general': [],
            'simplex': [],
            'trust_region': ['gn', 'hybrid'],
            'levenberg-marquardt': ['gn', 'gn_reg'],
            'gauss_newton': ['gn', 'gn_reg'],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': []}

    jacobian_enabled_solvers = ['gn', 'hybrid', 'gn_reg', 'hybrid_reg']

    hessian_enabled_solvers = ['hybrid', 'hybrid_reg']

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.param_ranges = None
        self._status = None
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
            raise UnknownMinimizerError(
                "No {} minimizer for RALFit".format(self.minimizer))

        if self.cost_func.hessian:
            self._options[b"exact_second_derivatives"] = True
        else:
            self._options[b"exact_second_derivatives"] = False

        # If parameter ranges have been set in problem, then set up bounds
        # option. For RALFit, this must be a 2 tuple array like object,
        # the first tuple containing the lower bounds for each parameter
        # and the second containing all upper bounds.
        if self.value_ranges is not None:
            value_ranges_lb, value_ranges_ub = zip(*self.value_ranges)
            self.param_ranges = (value_ranges_lb, value_ranges_ub)
        else:
            self.param_ranges = (
                [-np.inf]*len(self.initial_params),
                [np.inf]*len(self.initial_params))

    # pylint: disable=unused-argument
    def hes_eval(self, params, r):
        """
        Function to ensure correct inputs and outputs
        are used for the RALFit hessian evaluation

        :param params: parameters
        :type params: numpy array
        :param r: residuals, required by RALFit to
                  be passed for hessian evaluation
        :type r: numpy array
        :return: hessian 2nd order term: sum_{i=1}^m r_i \nabla^2 r_i
        :rtype: numpy array
        """
        H, _ = self.cost_func.hes_res(params)
        return np.matmul(H, r)
    # pylint: enable=unused-argument

    def fit(self):
        """
        Run problem with RALFit.
        """
        if self.cost_func.hessian:
            self._popt = ral_nlls.solve(self.initial_params,
                                        self.cost_func.eval_r,
                                        self.cost_func.jac_res,
                                        self.hes_eval,
                                        options=self._options,
                                        lower_bounds=self.param_ranges[0],
                                        upper_bounds=self.param_ranges[1])[0]
        else:
            self._popt = ral_nlls.solve(self.initial_params,
                                        self.cost_func.eval_r,
                                        self.cost_func.jac_res,
                                        options=self._options,
                                        lower_bounds=self.param_ranges[0],
                                        upper_bounds=self.param_ranges[1])[0]
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
