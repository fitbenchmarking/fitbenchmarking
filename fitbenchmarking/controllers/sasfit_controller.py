"""
Implements a controller for SASFit
"""

import numpy as np
import ctypes as ct
from ctypes import (
    c_int,
    c_float,
    c_bool,
    POINTER,
    Structure,
    CFUNCTYPE,
    byref,
)

from fitbenchmarking.controllers.base_controller import Controller


class sasfit_analytpar(Structure):
    _fields_ = []  # Probably okay to stay empty


class SASFIT_CData(Structure):
    _fields_ = [
        ("alpha", POINTER(POINTER(c_float))),
        ("covar", POINTER(POINTER(c_float))),
        ("oneda", POINTER(POINTER(c_float))),
        ("beta", POINTER(c_float)),
        ("a", POINTER(c_float)),
        ("da", POINTER(c_float)),
        ("atry", POINTER(c_float)),
        ("lista", POINTER(c_int)),
        ("ma", c_int),
        ("mfit", c_int),
        ("max_SD", c_int),
        ("chisq", c_float),
    ]


class SASFitController(Controller):
    """
    Controller for the SASFit fitting method.
    """

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
        self.lib = ct.CDLL("sasfit_controller/liblmfit.so")

        FUNCS_T = CFUNCTYPE(
            c_float,
            c_float,  # x_i
            c_float,  # res_i
            POINTER(c_float),  # a
            POINTER(c_float),  # ymod
            POINTER(c_float),  # dyda
            # c_int,                  # error_type
            # POINTER(c_bool)         # error
        )

        # ---- Bind the C functions ----
        self.lib.SASFITmrqmin.argtypes = [
            POINTER(c_float),
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

        ############################################################
        # Setup the problem
        ############################################################

        self.ndata = len(self.data_x)

        # ---- Outputs ----
        yfit_np = np.zeros(self.ndata, dtype=np.float32)
        res_np = np.zeros(self.ndata, dtype=np.float32)
        self.chisq = c_float(0.0)

        # ---- Convert numpy arrays to c float* ----
        self.x_ptr = self.data_x.ctypes.data_as(POINTER(c_float))
        self.y_ptr = self.data_y.ctypes.data_as(POINTER(c_float))
        self.sig_ptr = __.ctypes.data_as(
            POINTER(c_float)
        )  # FIXME: Do we read sigma in ??
        self.res_ptr = res_np.ctypes.data_as(POINTER(c_float))
        self.yfit_ptr = yfit_np.ctypes.data_as(POINTER(c_float))

        # ---- Other inputs for fitting ----
        # FIXME: below params are required to re-run the fit, but no
        # clue whether we can read them in from initial_params.
        # ma and mfit are n parameters and n fitted
        # defining some dummy here for simplicity
        self.ma = c_int(
            self.initial_params["n_params"]
        )  # n params  # FIXME: determine using len
        self.mfit = c_int(self.initial_params["n_fitted_params"])  # n fitted
        self.alamda = c_float(
            self.initial_params["alamda"]
        )  # Levenberg–Marquardt control parameter
        self.error_type = c_int(
            self.initial_params["error_type"]
        )  # this is 0-4 for linera, log, sqrt, poisson-like

        # ---- LM parameter arrays ----
        self.a_arr = (c_float * self.ma)(
            *[1.0, 1.0]
        )  # initial guess        # FIXME: Substitute with intial params
        self.da_arr = (c_float * self.ma)()
        self.atry_arr = (c_float * self.ma)()
        self.beta_arr = (c_float * self.mfit)()
        self.lista_arr = (c_int * self.mfit)(*list(range(self.mfit)))

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
            self.sig_ptr,  # signma values
            self.res_ptr,  # residuals
            self.yfit_ptr,  # model prediction
            c_int(self.ndata),
            self.a_arr,
            self.atry_arr,
            self.da_arr,
            self.beta_arr,
            c_int(self.ma),
            self.lista_arr,
            c_int(self.mfit),
            self.covar_mat,  # maybe should be byref
            self.alpha_mat,  # maybe should be byref
            self.oneda_mat,
            byref(self.chisq),  # Pointer to current chi‑square value
            self.cost_func.eval_cost,  # FIXME: this should have FUNC_T signature
            byref(self.alamda),  # Levenberg–Marquardt control parameter
            c_int(self.error_type),
            byref(c_bool(False)),  # Set to TRUE if anything goes wrong
        )

    def make_matrix_float(self, rows, cols):
        """
        Helper to create float** matrices
        Returns (mat_ptr, row_buffers) where:
        - mat_ptr is POINTER(POINTER(c_float)) suitable for passing to C as float**
        - row_buffers is a list you must KEEP referenced so memory isn't GC'd
        """
        RowArray = c_float * cols
        row_buffers = [RowArray() for _ in range(rows)]
        # Build array of row pointers
        MatArray = POINTER(c_float) * rows
        mat = MatArray(*[row_buffers[r] for r in range(rows)])
        return mat, row_buffers
