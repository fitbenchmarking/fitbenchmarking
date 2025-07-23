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

import numpy as np
import copy  # deepcopy
from aoclda.nonlinear_model import nlls

import traceback
# from fitbenchmarking.utils.log import get_logger
# LOGGER = get_logger()

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

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.VERBOSE = 0

        # AOCLDA data
        self._handle = None
        self._lb = None
        self._ub = None
        self._x = None
        self._status = None

    def eval_r(_, x, r, data) -> int:
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

    def jac_eval(_, x, J, data) -> int:
        """
        Function to ensure correct inputs and outputs
        are used for the AOCLDA jacobian evaluation

        :param x: coefficients
        :type x: numpy array
        :param J: output, jacobian 1nd order term
                  Store J update in-place.
        :type: numpy array
        :param data: alias to `self`
        :type: pointer
        :return: evaluation flag
        :rtype: int
        """

        # TODO jac_res returns a list of 1D numpy arrays
        J[:] = data.cost_func.jac_res(x)
        return 0

    def hes_eval(_, x, r, Hr, data) -> int:
        """
        Function to ensure correct inputs and outputs
        are used for the AOCLDA hessian evaluation

        :param x: coefficients
        :type x: numpy array
        :param r: residuals, required by AOCLDA to
                  be passed for hessian evaluation
        :param data: alias to `self`
        :type: pointer
        :type r: numpy array
        :param Hr: output, hessian 2nd order term
                   :math:`\\sum_{i=1}^m r_i \\nabla^2 r_i`.
                   Store Hr update in-place.
        :type: numpy array
        :return: evaluation flag
        :rtype: int
        """
        H, _ = data.cost_func.hes_res(x)
        Hr[:] = np.matmul(H, r)
        return 0

    def setup(self):
        """
        Setup for AOCLDA
        """

        n_coef = len(self.initial_params)
        n_res = len(self.data_y)
        # self.VERBOSE = 0 # inherit from -e parameter (print level 0..3)

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
            verbose=self.VERBOSE,
        )

    def fit(self):
        """
        Run problem with AOCLDA.
        """

        maxit = 500  # Same as RALFit
        ftol = 1e-8  # TODO how to pass this option?
        abs_ftol = 1e-8  # TODO how to pass this option?
        gtol = 1e-8  # TODO how to pass this option?
        abs_gtol = 1e-5  # TODO how to pass this option?
        xtol = 2.22e-16  # TODO how to pass this option?

        use_fd = False  # TODO how to pass this option?
        fd_step = 1e-7  # TODO how to pass this option?
        fd_ttol = 1e-4  # TODO how to pass this option?

        if self.cost_func.jacobian and not use_fd:
            jac = self.jac_eval  # AOCLDA wrapper to self.cost_func.jac_res
        else:
            jac = None  # Request finite-differences

        if self.cost_func.hessian:
            hes = self.hes_eval  # AOCLDA wrapper to self.cost_func.hessian
        else:
            hes = None

        self._x = np.array(
            self.initial_params
        )  # x has to be np.array and is overwritten!

        try:
            self._handle.fit(
                x=self._x,
                fun=self.eval_r,
                jac=jac,
                hes=hes,
                hep=None,
                data=self,
                maxit=maxit,
            )
        # ftol=ftol,
        # abs_ftol=abs_ftol,
        # gtol=gtol,
        # abs_gtol,
        # xtol=xtol,
        # fd_step=fd_step,
        # fd_ttol=fd_ttol)

        except RuntimeWarning:  # FIXME this is not caught
            #    2: Software run but didn’t converge to solution
            #    6: Solver has exceeded maximum allowed runtime
            self._status = 2
        except Exception as e:
            if self.VERBOSE > 0:
                print(e)
                print(traceback.format_exc())
            self._status = 3  # Software raised an exception
        else:
            #    0: Successfully converged
            #    1: Software reported maximum number of iterations exceeded
            #    5: Solution doesn’t respect parameter bounds
            ok = True
            if self._lb is not None:
                ok = ok and all(self._lb <= x)
            if self._ub is not None:
                ok = ok and all(self._ub >= x)

            if maxit <= self._handle.n_iter:
                self._status = 1
            elif not ok:
                self._status = 5
            else:
                self._status = 0

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        if (
            self._status == 0
            or self._status == 1
            or self._status == 2
            or self._status == 5
        ):
            self.iteration_count = self._handle.n_iter
            self.func_evals = self._handle.n_eval[
                "f"
            ]  # 'j', 'h', 'hp', 'fd_f' as well available

        # Final Params: The final values for the params from the minimizer
        self.final_params = self._x.tolist()

        # Flag: error handling flag
        self.flag = self._status
