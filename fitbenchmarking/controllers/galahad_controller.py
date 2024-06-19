"""
Implements a controller for the GALAHAD fitting software.
"""
from typing import Any, Callable, Dict

import numpy as np
from galahad import arc, bllsb, nls, tru

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import IncompatibleMinimizerError


class GalahadController(Controller):
    """
    Controller for the GALAHAD fitting software.
    """

    algorithm_check = {
        "all": ["arc", "bllsb", "nls", "tru"],
        "ls": ["bllsb", "nls"],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": ["tru"],
        "levenberg-marquardt": [],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": []}

    jacobian_enabled_solvers = ["arc", "bllsb", "nls", "tru"]

    hessian_enabled_solvers = ["arc", "bllsb", "nls", "tru"]

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.no_bounds_minimizers = []

        self._num_vars = len(self.cost_func.problem.param_names)
        self._hessian: "Callable" = self._noop
        self._initial_params_array = np.zeros(self._num_vars)
        self._module = arc
        self._nlls = False
        self._jacobian = self.cost_func.jac_cost
        self._P = self._eval_hes_res_product
        self._result = [0]

    def setup(self):
        """
        Setup problem ready to be run with GALAHAD
        """
        self._module = {
            "arc": arc,
            "bllsb": bllsb,
            "nls": nls,
            "tru": tru,
        }[self.minimizer]

        if self.minimizer in self.algorithm_check["ls"]:
            if isinstance(self.cost_func, BaseNLLSCostFunc):
                self._nlls = True
            else:
                raise IncompatibleMinimizerError(
                    f"The minimizer {self.minimizer} can only be used for "
                    "least squares problems"
                )
        else:
            self._nlls = False

        print(f"Running: opts = {self.minimizer}.initialize()")
        opts = self._module.initialize()
        kwargs: "Dict[str, Any]" = {
            "n": self._num_vars,
            "options": opts,
            "H_ne": 10,
            "H_row": None,
            "H_col": None,
            "H_ptr": None,
        }

        has_hessian = self.cost_func.hessian is not None
        if has_hessian:
            self._hessian = self._hes
            kwargs["H_type"] = "dense"
            if self._nlls:
                kwargs.update({
                    "P_type": "dense_by_columns",
                    "P_ne": 10,
                    "P_row": None,
                    "P_col": None,
                    "P_ptr": None,
                })
                self._P = self._eval_hes_res_product
        else:
            self._hessian = self._noop
            kwargs["H_type"] = "absent"

        if self._nlls:
            self._jacobian = self._jac
            kwargs.update({
                "m": self.data_x.shape[0],
                "J_type": "dense",
                "J_ne": 10,
                "J_row": None,
                "J_col": None,
                "J_ptr": None,
                "w": np.ones(self.data_x.shape[0]),
            })
        else:
            self._jacobian = self.cost_func.jac_cost

        print(f"Running: {self.minimizer}.load(**kwargs)")
        self._module.load(**kwargs)

        self._initial_params_array = np.array(self.initial_params)

    def fit(self):
        """
        Run problem with GALAHAD.
        """
        args = []
        if not self._nlls:
            args = [
                self._num_vars,  # n
                int(self._num_vars*(self._num_vars+1)/2),  # H_ne
                self._initial_params_array,  # x
                self.cost_func.eval_cost,  # eval_f
                self._jacobian,  # eval_g
                self._hessian,  # eval_h
            ]
        else:
            m = self.data_x.shape[0]
            args = [
                self._num_vars,  # n
                m,  # m
                self._initial_params_array,  # x
                self.cost_func.eval_r,  # eval_c
                self._num_vars*m,  # j_ne
                self._jacobian,  # eval_j
                int(self._num_vars*(self._num_vars+1)/2),  # h_ne
                self._hessian,  # eval_h
                self._num_vars*m,  # p_ne
                self._P,  # evalhprod
            ]

        print(f"Running: self.result = {self.minimizer}.solve(*args)")
        self._result = self._module.solve(*args)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        status_map = {0: 0,  # Success
                      -1: 3,  # Alloc error
                      -2: 3,  # Dealloc error
                      -3: 3,  # Bad hessian format
                      -7: 3,  # Unbounded objective
                      -9: 3,  # Analysis failed       (linear solve)
                      -10: 3,  # Factorisation failed (linear solve)
                      -11: 3,  # Solve failed         (linear solve)
                      -16: 2,  # Ill-conditioned
                      -18: 1,  # Too many iterations
                      -19: 3,  # Max runtime
                      -82: 3,  # Killed by user
                      }
        print(f"Running: info = {self.minimizer}.information()")
        info = self._module.information()
        print(f"Running: {self.minimizer}.terminate()")
        self._module.terminate()
        self.final_params = self._result[0]
        self.flag = status_map[info["status"]]

    def _jac(self, p):
        tmp: "np.ndarray" = self.cost_func.jac_res(p)
        return np.ravel(tmp)

    def _hes(self, p):
        tmp: "np.ndarray" = self.cost_func.hes_cost(p)
        return tmp[np.tril_indices(tmp.shape[0])]

    def _eval_hes_res_product(self, p, v):
        H, _ = self.cost_func.hes_res(p)
        n = len(v)
        P = np.zeros(n*H.shape[-1])
        for i in range(H.shape[-1]):
            P[i*n:(i+1)*n] = np.dot(H[..., i], v)

        return P

    def _noop(self, *args):
        return None
