"""
Implements a controller for SASFit
"""

import ctypes as ct
from ctypes import (
    CFUNCTYPE,
    POINTER,
    byref,
    c_bool,
    c_float,
    c_int,
)

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


class SASFitController(Controller):
    """
    Controller for the SASFit fitting method.
    """

    controller_name = "sasfit"
    algorithm_check = {
        "all": ["lm-sasfit"],
    }

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
        # Load library
        self.lib = ct.CDLL(
            "/home/letizia/fitbenchmarking_new/fitbenchmarking/fitbenchmarking/controllers/sasfit_controller/liblmfit.so"
        )

        # ---- Bind the C functions ----
        self.lib.SASFITmrqmin.argtypes = [
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
        self.lib.SASFITmrqmin.restype = None

        self.lib.SASFITmrqcof.argtypes = [
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
        self.lib.SASFITmrqcof.restype = None

        self.lib.SASFITgaussj.argtypes = [
            POINTER(POINTER(c_float)),
            c_int,
            POINTER(POINTER(c_float)),
            c_int,
            POINTER(c_bool),
        ]
        self.lib.SASFITgaussj.restype = None

        self.lib.SASFITcovsrt.argtypes = [
            POINTER(POINTER(c_float)),
            c_int,
            POINTER(c_int),
            c_int,
            POINTER(c_bool),
        ]
        self.lib.SASFITcovsrt.restype = None

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

    def fit(self):
        """
        Run problem
        """

        self.lib.SASFITmrqmin(
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
            self.make_funcs_wrapper(self.cost_func),  # the model function
            byref(self.alamda),  # Levenberg Marquardt control parameter
            c_int(self.error_type),  # 0 to 4
            byref(c_bool(False)),  # Set to TRUE if anything goes wrong
        )

        self._popt = self.ptr_to_numpy(self.a_arr, self.ma)

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
        def funcs_wrapper(x_i, a_ptr, ymod_ptr, dyda_ptr):
            # need this for getting the right jac later
            idx = int(np.where(self.data_x == x_i)[0][0])

            # extract params correctly
            params = [float(a_ptr[i]) for i in range(self.n_params)]

            # compute model
            y = float(
                cost_func.problem.eval_model(x=np.array(x_i), params=params)
            )
            ymod_ptr[0] = y

            # compute jacobian
            jac = cost_func.jac_res(params)

            for i in range(self.n_params):
                dyda_ptr[i] = np.asarray(jac[idx][i], dtype=np.float32)

            return y

        return FUNCS_T(funcs_wrapper)

    def ptr_to_numpy(self, ptr, length) -> np.ndarray:
        # Create a 1D numpy array that views the same memory
        return np.ctypeslib.as_array(ptr, shape=(length,))

    def cleanup(self):
        # max_iters_messages = [
        #     "maximum number of iterations",
        #     "iteration limit reached",
        #     "iterations reached limit",
        # ]

        # if self.result.success:
        #     self.flag = 0
        # elif any(
        #     message in self.result.message.lower()
        #     for message in max_iters_messages
        # ):
        #     self.flag = 1
        # else:
        #     self.flag = 2

        # if "nfev" in self.result:
        #     self.func_evals = self.result.nfev
        # if "nit" in self.result:
        #     self.iteration_count = self.result.nit
        self.flag = 0
        self.final_params = self._popt
