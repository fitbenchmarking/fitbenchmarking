# Copyright (c) 2025 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
############################################################

"""
Implements a controller for AMD AOCL Data Analytics NLLS solver
https://github.com/amd/aocl-data-analytics
"""

import warnings

import numpy as np
from aoclda.nonlinear_model import nlls

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class AOCLDAController(Controller):
    """
    Controller for the AOCLDA NLLS fitting software.
    """

    algorithm_check = {
        "all": [
            "gn",
            "hybrid",
            "newton",
            "newton-tensor",
            "gn_reg",
            "hybrid_reg",
            "newton_reg",
            "newton-tensor_reg",
        ],
        "ls": [
            "gn",
            "hybrid",
            "newton",
            "newton-tensor",
            "gn_reg",
            "hybrid_reg",
            "newton_reg",
            "newton-tensor_reg",
        ],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": ["gn", "hybrid", "newton", "newton-tensor"],
        "levenberg-marquardt": ["gn", "gn_reg"],
        "gauss_newton": ["gn", "gn_reg"],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = [
        "gn",
        "hybrid",
        "newton",
        "newton-tensor",
        "gn_reg",
        "hybrid_reg",
        "newton_reg",
        "newton-tensor_reg",
    ]

    hessian_enabled_solvers = [
        "hybrid",
        "newton",
        "newton-tensor",
        "hybrid_reg",
        "newton_reg",
        "newton-tensor_reg",
    ]

    support_for_bounds = True

    # Text used to identify the warnings raised by the solver
    _SOLVER_WARNING = "RALFit solver warning message"
    _MAX_ITERATIONS = "Maximum number of iterations"

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        # AOCLDA data
        self._handle = None
        self._lb = None
        self._ub = None
        self._x = None
        self._warnings = None

        # Same as the RALFit controller, all other stopping tolerances use
        # the solver defaults (which match the RALFit defaults)
        self.maxit = 500

    def eval_r(self, x, r, data) -> int:
        """
        Function to ensure correct inputs and outputs
        are used for the AOCLDA residual evaluation

        :param x: coefficients
        :type x: numpy array
        :param r: output, residual term
                  Store r update in-place.
        :type: numpy array
        :param data: alias to `self`
        :type: pointer
        :return: evaluation flag
        :rtype: int
        """
        r[:] = data.cost_func.eval_r(x)
        return 0

    def jac_eval(self, x, jac, data) -> int:
        """
        Function to ensure correct inputs and outputs
        are used for the AOCLDA jacobian evaluation

        :param x: coefficients
        :type x: numpy array
        :param jac: output, jacobian 1st order term
                    Store jac update in-place.
        :type: numpy array
        :param data: alias to `self`
        :type: pointer
        :return: evaluation flag
        :rtype: int
        """
        jac[:] = data.cost_func.jac_res(x)
        return 0

    def hes_eval(self, x, r, hr, data) -> int:
        """
        Function to ensure correct inputs and outputs
        are used for the AOCLDA hessian evaluation

        :param x: coefficients
        :type x: numpy array
        :param r: residuals, required by AOCLDA to
                  be passed for hessian evaluation
        :type r: numpy array
        :param hr: output, hessian 2nd order term
                   :math:`\\sum_{i=1}^m r_i \\nabla^2 r_i`.
                   Store hr update in-place.
        :type: numpy array
        :param data: alias to `self`
        :type: pointer
        :return: evaluation flag
        :rtype: int
        """
        hes, _ = data.cost_func.hes_res(x)
        hr[:] = np.matmul(hes, r)
        return 0

    def setup(self):
        """
        Setup for AOCLDA
        """

        n_coef = len(self.initial_params)
        n_res = len(self.data_y)
        verbose = 0

        # Use bytestrings explicitly as python 3 defaults to unicode.
        if self.minimizer == "gn":
            model = b"gauss-newton"  # self._options[b"model"] = 1
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"tr"  # self._options[b"type_of_method"] = 1
        elif self.minimizer == "gn_reg":
            model = b"gauss-newton"  # self._options[b"model"] = 1
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"reg"  # self._options[b"type_of_method"] = 2
        elif self.minimizer == "hybrid":
            model = b"hybrid"  # self._options[b"model"] = 3
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"tr"  # self._options[b"type_of_method"] = 1
        elif self.minimizer == "hybrid_reg":
            model = b"hybrid"  # self._options[b"model"] = 3
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"reg"  # self._options[b"type_of_method"] = 2
        elif self.minimizer == "newton":
            model = b"quasi-newton"  # self._options[b"model"] = 2
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"tr"  # self._options[b"type_of_method"] = 1
        elif self.minimizer == "newton_reg":
            model = b"quasi-newton"  # self._options[b"model"] = 2
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"reg"  # self._options[b"type_of_method"] = 2
        elif self.minimizer == "newton-tensor":
            model = b"tensor-newton"  # self._options[b"model"] = 4
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"tr"  # self._options[b"type_of_method"] = 1
        elif self.minimizer == "newton-tensor_reg":
            model = b"tensor-newton"  # self._options[b"model"] = 4
            method = b"galahad"  # self._options[b"nlls_method"] = 4
            glob_strategy = b"reg"  # self._options[b"type_of_method"] = 2
        else:
            raise UnknownMinimizerError(
                f"No {self.minimizer} minimizer for AOCLDA"
            )

        # If parameter ranges have been set in problem, then set up bounds
        # option. For AOCLDA, this must be a 2 tuple array like object,
        # the first tuple containing the lower bounds for each parameter
        # and the second containing all upper bounds.
        if self.value_ranges is not None:
            self._lb, self._ub = zip(*self.value_ranges)

        self._handle = nlls(
            n_coef=n_coef,
            n_res=n_res,
            weights=None,
            lower_bounds=self._lb,
            upper_bounds=self._ub,
            order="c",
            model=model,
            method=method,
            glob_strategy=glob_strategy,
            verbose=verbose,
        )

        # Set initial iterate
        self._x = np.array(
            self.initial_params
        )  # x has to be np.array and is overwritten!

    def fit(self):
        """
        Run problem with AOCLDA.
        Note: only this method is timed
        """
        # Only use exact second derivatives if a Hessian is available
        hes = self.hes_eval if self.cost_func.hessian else None

        with warnings.catch_warnings(record=True) as self._warnings:
            # Record every warning, regardless of any filters set elsewhere.
            # Solver raises RuntimeWarning for
            # 1: Software reported maximum number of iterations exceeded
            # 2: Software run but didn't converge to solution
            # these are handled in cleanup
            warnings.simplefilter("always")
            self._handle.fit(
                x=self._x,
                fun=self.eval_r,
                jac=self.jac_eval,
                hes=hes,
                hep=None,
                data=self,
                maxit=self.maxit,
            )

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        # Only warnings raised by the solver are considered, any other
        # warnings (e.g. numpy overflow when evaluating the model) are ignored
        solver_messages = [
            str(warning.message)
            for warning in self._warnings or []
            if issubclass(warning.category, RuntimeWarning)
            and self._SOLVER_WARNING in str(warning.message)
        ]

        self.flag = 0
        for message in solver_messages:
            if self._MAX_ITERATIONS in message:
                self.flag = 1
            else:
                self.flag = 2
                break

        self.iteration_count = self._handle.n_iter
        self.func_evals = self._handle.n_eval["f"]  # "fd_f" also available

        # Final Params: The final values for the params from the minimizer
        self.final_params = self._x.tolist()
