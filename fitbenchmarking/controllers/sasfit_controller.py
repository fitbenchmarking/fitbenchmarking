"""
Implements a controller for SASFit
"""

import ctypes as ct
import os
from ctypes import (
    CFUNCTYPE,
    POINTER,
    byref,
    c_bool,
    c_float,
    c_int,
)
from pathlib import Path

import numpy as np

from fitbenchmarking.controllers.base_controller import Controller

FUNCS_T = CFUNCTYPE(
    c_float,
    c_float,  # x_i
    POINTER(c_float),  # a
    POINTER(c_float),  # ymod
    POINTER(c_float),  # dyda
    # c_int,                  # error_type
    # POINTER(c_bool)         # error
)

#: Location of the SASfit Levenberg-Marquardt shared library. Defaults to
#: 'liblmfit.so' shipped alongside this controller, and can be overridden
#: with the 'SASFIT_LM_LIB' environment variable.
LIB_PATH = Path(
    os.environ.get(
        "SASFIT_LM_LIB",
        Path(__file__).parent / "sasfit_controller" / "liblmfit.so",
    )
)


def load_library(path):
    """
    Load the SASfit Levenberg-Marquardt shared library and declare the
    signatures of the functions it provides.

    :param path: Location of the shared library
    :type path: pathlib.Path

    :return: The loaded shared library
    :rtype: ctypes.CDLL
    """
    if not path.is_file():
        raise ImportError(
            f"Could not find the SASfit LM shared library at '{path}'. "
            "Build 'liblmfit.so' from the SASfit LM sources, then either "
            "place it at that location or point the 'SASFIT_LM_LIB' "
            "environment variable at it."
        )

    try:
        lib = ct.CDLL(str(path))
    except OSError as excp:
        raise ImportError(
            f"Could not load the SASfit LM shared library at '{path}': {excp}"
        ) from excp

    lib.SASFITmrqmin.argtypes = [
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        c_int,
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        c_int,
        POINTER(c_int),
        c_int,
        POINTER(POINTER(c_float)),
        POINTER(POINTER(c_float)),
        POINTER(POINTER(c_float)),
        POINTER(c_float),
        FUNCS_T,
        POINTER(c_float),
        c_int,
        POINTER(c_bool),
    ]
    lib.SASFITmrqmin.restype = None

    lib.SASFITmrqcof.argtypes = [
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        POINTER(c_float),
        c_int,
        POINTER(c_float),
        POINTER(c_int),
        c_int,
        c_int,
        c_int,
        POINTER(POINTER(c_float)),
        POINTER(c_float),
        POINTER(c_float),
        FUNCS_T,
        POINTER(c_bool),
    ]
    lib.SASFITmrqcof.restype = None

    lib.SASFITgaussj.argtypes = [
        POINTER(POINTER(c_float)),
        c_int,
        POINTER(POINTER(c_float)),
        c_int,
        POINTER(c_bool),
    ]
    lib.SASFITgaussj.restype = None

    lib.SASFITcovsrt.argtypes = [
        POINTER(POINTER(c_float)),
        c_int,
        POINTER(c_int),
        c_int,
        POINTER(c_bool),
    ]
    lib.SASFITcovsrt.restype = None

    return lib


LIB = load_library(LIB_PATH)


class SASFitController(Controller):
    """
    Controller for the SASFit fitting method.
    """

    controller_name = "sasfit"

    algorithm_check = {
        "all": ["lm-sasfit"],
        "ls": ["lm-sasfit"],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": ["lm-sasfit"],
        "levenberg-marquardt": ["lm-sasfit"],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = ["lm-sasfit"]

    #: Most Levenberg-Marquardt iterations to run before giving up
    max_iterations = 500

    #: Relative change in chi squared below which an iteration is taken
    #: to have made no progress
    tolerance = 1e-8

    #: Iterations without progress needed before the fit is taken to
    #: have converged
    required_no_progress = 4

    #: Value of 'alamda' above which the steps on offer are too small to
    #: be worth taking
    max_alamda = 1e12

    def __init__(self, cost_func):
        """
        Extract param names for function setup

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

    def setup(self):
        """
        Setup problem ready to be run
        """
        self.n_params = len(self.initial_params)
        self.n_fitted_params = len(self.initial_params)

        ############################################################
        # Setup the problem
        ############################################################

        self.ndata = len(self.data_x)

        # ---- Outputs ----
        yfit_np = np.zeros(self.ndata, dtype=np.float32)
        self.chisq = c_float(0.0)

        # ---- Convert numpy arrays to c float* ----
        self.data_x_np = np.asarray(self.data_x, dtype=np.float32, order="C")
        self.data_y_np = np.asarray(self.data_y, dtype=np.float32, order="C")
        self.data_e_np = np.asarray(self.data_e, dtype=np.float32, order="C")

        # Used by the model callback to find the Jacobian row for the
        # point it has been given
        self.x_index = {float(x): i for i, x in enumerate(self.data_x_np)}

        self.x_ptr = self.data_x_np.ctypes.data_as(POINTER(c_float))
        self.y_ptr = self.data_y_np.ctypes.data_as(POINTER(c_float))
        self.sig_ptr = self.data_e_np.ctypes.data_as(
            POINTER(c_float)
        )  # FIXME: standard deviation
        self.yfit_ptr = yfit_np.ctypes.data_as(POINTER(c_float))

        # ---- Other inputs for fitting ----
        # FIXME: below params are required to run the fit
        self.ma = self.n_params  # n total params (fitted and not)
        self.mfit = self.n_fitted_params
        self.alamda = c_float(
            -1.0
        )  # LM control parameter, just needs to be < 0
        self.error = c_bool(False)

        # error_type controls how the data (y) and model outputs (ymod) are
        # transformed before computing residuals and χ²
        # It's 0-4 for linear, log, sqrt, poisson-like
        self.error_type = 0  # FIXME: should the user give this?

        # ---- LM parameter arrays ----
        self.a_arr = (c_float * self.ma)(
            *self.initial_params
        )  # e.g. (c_float * self.ma)(*[1.0, 1.0])
        self.da_arr = (c_float * self.ma)()  # proposed parameter changes
        self.atry_arr = (c_float * self.ma)()  # the trial parameter vector
        self.beta_arr = (c_float * self.mfit)()  # the gradient vector
        self.lista_arr = (c_int * self.mfit)(*range(self.mfit))

        # ---- Matrices: alpha, covar (mfit x mfit), oneda (mfit x 1) ----
        self.alpha_mat, _ = self.make_matrix_float(self.mfit, self.mfit)
        self.covar_mat, _ = self.make_matrix_float(self.mfit, self.mfit)
        self.oneda_mat, _ = self.make_matrix_float(self.mfit, 1)

        # ---- Model function ----
        # Held on the controller so that the callback stays alive for as
        # long as the library might call it
        self.funcs_cb = self.make_funcs_wrapper(self.cost_func)

    def fit(self):
        """
        Run problem

        A call to 'SASFITmrqmin' carries out a single Levenberg-Marquardt
        iteration, so it is called repeatedly until chi squared stops
        improving. Once that happens a final iteration is run with
        'alamda' set to zero, which fills in the covariance matrix.

        An iteration which improves chi squared is taken by the library,
        which lowers 'alamda'. One which doesn't is thrown away and
        'alamda' is raised instead, so it is only worth stopping on the
        iterations that were taken.
        """
        self.iteration_count = 0
        self.func_evals = 0
        no_progress = 0
        prev_chisq = np.inf
        self._status = 1

        while self.iteration_count < self.max_iterations:
            prev_alamda = self.alamda.value
            self.mrqmin()
            self.iteration_count += 1

            if self.error.value:
                self._status = 2
                break

            chisq = self.chisq.value
            improvement = prev_chisq - chisq
            prev_chisq = chisq

            # 'alamda' is lowered when a step is taken and raised when it
            # is thrown away. It starts out negative to ask for the set up
            # to be done, so only a positive value says anything
            if 0.0 < prev_alamda < self.alamda.value:
                # The step was thrown away. Keep going with a bigger
                # 'alamda' until it is too big to give a usable step
                if self.alamda.value > self.max_alamda:
                    self._status = 0
                    break
            elif improvement <= self.tolerance * abs(chisq):
                no_progress += 1
                if no_progress >= self.required_no_progress:
                    self._status = 0
                    break
            else:
                no_progress = 0

            self.timer.check_elapsed_time()

        if self._status == 0:
            self.alamda = c_float(0.0)
            self.mrqmin()

        self._popt = self.ptr_to_numpy(self.a_arr, self.ma)

    def mrqmin(self):
        """
        Run a single Levenberg-Marquardt iteration.
        """
        LIB.SASFITmrqmin(
            self.x_ptr,  # x values
            self.y_ptr,  # measured y
            self.sig_ptr,  # standard dev
            self.yfit_ptr,  # model prediction
            c_int(self.ndata),  # n data
            self.a_arr,  # initial params
            self.atry_arr,
            self.da_arr,
            self.beta_arr,
            c_int(self.ma),  # n total params
            self.lista_arr,  # param idx mapping arr, track which params fitted
            c_int(self.mfit),  # n fitted params
            self.covar_mat,  # working space array
            self.alpha_mat,  # working space array
            self.oneda_mat,  # working space array
            byref(self.chisq),  # Pointer to current chi square value
            self.funcs_cb,  # the model function
            byref(self.alamda),  # Levenberg Marquardt control parameter
            c_int(self.error_type),  # 0 to 4
            byref(self.error),  # Set to TRUE if anything goes wrong
        )

    def make_matrix_float(self, rows, cols):
        """
        Helper to create float** matrices
        Returns (mat_ptr, row_buffers) where:
        - mat_ptr is POINTER(POINTER(c_float)) suitable for passing
          to C as float**
        - row_buffers is a list you must KEEP referenced so memory isn't GC'd
        """
        RowArray = c_float * cols
        row_buffers = [RowArray() for _ in range(rows)]
        # Build array of row pointers
        MatArray = POINTER(c_float) * rows
        mat = MatArray(*[row_buffers[r] for r in range(rows)])
        return mat, row_buffers

    def make_funcs_wrapper(self, cost_func):
        """
        Build the callback used by the library to evaluate the model and
        its derivatives at a single x value.

        The library asks for one data point at a time, but the model and
        its Jacobian are much cheaper to evaluate for the whole data set at
        once, so they are evaluated once per set of parameters and cached.
        The row needed by the current point is then picked out by index.

        :param cost_func: Cost function providing the model and Jacobian.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        :return: The callback in the form expected by the library
        :rtype: ctypes function pointer
        """
        cache = {"params": None, "ymod": None, "jac": None}

        def funcs_wrapper(x_i, a_ptr, ymod_ptr, dyda_ptr):
            # The parameters the library wants the model evaluated at
            params = [float(a_ptr[i]) for i in range(self.n_params)]

            # x_i is passed straight back from the data, so it is usually
            # one of the values the index was built from
            idx = self.x_index.get(x_i)

            if idx is None:
                # Somewhere other than a data point, so it has to be
                # worked out on its own
                x_arr = np.array([x_i])
                y = float(cost_func.problem.eval_model(params, x=x_arr)[0])
                dyda = cost_func.jacobian.eval(params, x=x_arr)[0]
            else:
                if params != cache["params"]:
                    cache["ymod"] = cost_func.problem.eval_model(
                        params, x=self.data_x
                    )
                    cache["jac"] = cost_func.jacobian.eval(
                        params, x=self.data_x
                    )
                    cache["params"] = params
                    # One set of parameters is one evaluation of the model
                    # over the whole data set
                    self.func_evals += 1

                y = float(cache["ymod"][idx])
                dyda = cache["jac"][idx]

            ymod_ptr[0] = y
            for i in range(self.n_params):
                dyda_ptr[i] = float(dyda[i])

            return y

        return FUNCS_T(funcs_wrapper)

    def ptr_to_numpy(self, ptr, length) -> np.ndarray:
        # Create a 1D numpy array that views the same memory
        return np.ctypeslib.as_array(ptr, shape=(length,))

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables
        results will be read from.
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 1:
            self.flag = 1
        else:
            self.flag = 3

        self.final_params = self._popt
