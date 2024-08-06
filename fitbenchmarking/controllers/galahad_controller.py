"""
Implements a controller for the GALAHAD fitting software.
"""
from typing import Any, Callable, Dict

import numpy as np
from galahad import arc, bgo, dgo, nls, trb, tru

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import IncompatibleMinimizerError


class GalahadController(Controller):
    """
    Controller for the GALAHAD fitting software.
    """

    algorithm_check = {
        "all": ["arc", "bgo", "dgo", "nls", "trb", "tru"],
        "ls": ["nls"],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": ["trb", "tru"],
        "levenberg-marquardt": [],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": ["bgo", "dgo"],
        "MCMC": []}

    jacobian_enabled_solvers = ["arc", "bgo", "dgo", "nls", "trb", "tru"]
    hessian_enabled_solvers = ["arc", "bgo", "dgo", "nls", "trb", "tru"]

    support_for_bounds = True
    no_bounds_minimizers = ["arc", "tru", "nls"]
    bounds_required_minimizers = ["bgo", "dgo"]

    def __init__(self, cost_func):
        """
        Initialises variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """
        super().__init__(cost_func)

        self._num_vars = len(self.cost_func.problem.param_names)
        self._hessian: "Callable" = self._noop
        self._initial_params_array = np.zeros(self._num_vars)
        self._module = arc
        self._jacobian = self.cost_func.jac_cost
        self._P = self._eval_hes_res_product
        self._result = [0]
        self._minimizer = ""
        self._variant = ""

    def setup(self):
        """
        Setup problem ready to be run with GALAHAD
        """
        minimizer: "str" = self.minimizer
        variant: "str" = ""
        try:
            minimizer, variant = minimizer.split("_", 1)
        except ValueError:
            pass

        self._module = {
            "arc": arc,
            "bgo": bgo,
            "dgo": dgo,
            "nls": nls,
            "trb": trb,
            "tru": tru,
        }[minimizer]

        has_hessian = self.cost_func.hessian is not None
        self._jacobian = self.cost_func.jac_cost

        x_l, x_u = ([], [])
        if self.value_ranges is None:
            x_l = np.repeat(-np.inf, self._num_vars)
            x_u = np.repeat(np.inf, self._num_vars)
        else:
            x_l, x_u = zip(*self.value_ranges)

        x_l = np.array(x_l)
        x_u = np.array(x_u)

        opts = self._module.initialize()
        kwargs: "Dict[str, Any]" = {
                "options": opts,
        }

        if minimizer in ["arc", "tru"]:
            kwargs.update({
                "n": self._num_vars,
                "H_type": "dense" if has_hessian else "absent",
                "H_ne": 10,
                "H_row": None,
                "H_col": None,
                "H_ptr": None,
            })
        elif minimizer in ["bgo", "dgo", "trb"]:
            kwargs.update({
                "n": self._num_vars,
                "x_l": x_l,
                "x_u": x_u,
                "H_type": "dense" if has_hessian else "absent",
                "H_ne": 10,
                "H_row": None,
                "H_col": None,
                "H_ptr": None,
            })

        elif minimizer in ["nls"]:
            if not has_hessian:
                raise IncompatibleMinimizerError(
                    "Requires hessian information (for now)")
            kwargs.update({
                "n": self._num_vars,
                "m": self.data_x.shape[0],
                "J_type": "dense",
                "J_ne": 10,
                "J_row": None,
                "J_col": None,
                "J_ptr": None,
                "H_type": "dense",
                "H_ne": 10,
                "H_row": None,
                "H_col": None,
                "H_ptr": None,
                "w": np.ones(self.data_x.shape[0]),
                "P_type": "dense_by_columns",
                "P_ne": 10,
                "P_row": None,
                "P_col": None,
                "P_ptr": None,
            })
            self._jacobian = self._jac

        if has_hessian:
            self._hessian = self._hes
            self._P = self._eval_hes_res_product
        else:
            self._hessian = self._noop

        self._module.load(**kwargs)

        self._initial_params_array = np.array(self.initial_params)
        self._minimizer = minimizer
        self._variant = variant

    def fit(self):
        """
        Run problem with GALAHAD.
        """
        kwargs = {}
        if self._minimizer in ["arc", "bgo", "dgo", "trb", "tru"]:
            kwargs = {
                "n": self._num_vars,
                "H_ne": int(self._num_vars*(self._num_vars+1)/2),
                "x": self._initial_params_array,
                "eval_f": self.cost_func.eval_cost,
                "eval_g": self._jacobian,
                "eval_h": self._hessian,
            }
        elif self._minimizer in ["nls"]:
            m = self.data_x.shape[0]
            kwargs = {
                "n": self._num_vars,
                "m": m,
                "x": self._initial_params_array,
                "eval_c": self.cost_func.eval_r,
                "J_ne": self._num_vars*m,
                "eval_j": self._jacobian,
                "H_ne": int(self._num_vars*(self._num_vars+1)/2),
                "eval_h": self._hessian,
                "P_ne": self._num_vars*m,
                "eval_hprod": self._P,
            }

        self._result = self._module.solve(**kwargs)

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
                      -15: 3,  # Preconditioner not pos def
                      -16: 2,  # Ill-conditioned
                      -18: 1,  # Too many iterations
                      -19: 3,  # Max runtime
                      -82: 3,  # Killed by user
                      }
        info = self._module.information()
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
