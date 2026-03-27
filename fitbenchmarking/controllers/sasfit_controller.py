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
    CFUNCTYPE,
    byref,
)

from fitbenchmarking.controllers.base_controller import Controller


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

        ############################################################
        # Setup the problem
        ############################################################

        self.ndata = len(self.data_x)

        # ---- Outputs ----
        yfit_np = np.zeros(self.ndata, dtype=np.float32)
        self.chisq = c_float(0.0)

        # ---- Convert numpy arrays to c float* ----
        self.x_ptr = self.data_x.ctypes.data_as(POINTER(c_float))
        self.y_ptr = self.data_y.ctypes.data_as(POINTER(c_float))
        self.sig_ptr = self.data_e.ctypes.data_as(
            POINTER(c_float)
        )  # FIXME: standard deviation -- do we have this? Is it data_e?
        self.yfit_ptr = yfit_np.ctypes.data_as(POINTER(c_float))

        # ---- Other inputs for fitting ----
        # FIXME: below params are required to run the fit, but 
        # can we read them in from initial_params?
        # ma and mfit are n parameters and n fitted
        # defining some dummy here for simplicity
        self.ma = c_int(
            self.initial_params["n_params"]
        )  # n total params (fitted and not)  # FIXME: determine using len ?
        self.mfit = c_int(self.initial_params["n_fitted_params"])  
        self.alamda = c_float(-1)  # LM control parameter, just needs to be < 0

        
        # error_type controls how the data (y) and model outputs (ymod) are 
        # transformed before computing residuals and χ²
        # It's 0-4 for linear, log, sqrt, poisson-like
        self.error_type = c_int(
            self.initial_params["error_type"]  # FIXME: do we ask the user to give this?
        )  

        # ---- LM parameter arrays ----      
        self.a_arr = (c_float * self.ma)(*self.initial_params)  # e.g. (c_float * self.ma)(*[1.0, 1.0])
        self.da_arr = (c_float * self.ma)()  # proposed parameter changes
        self.atry_arr = (c_float * self.ma)()  # the trial parameter vector
        self.beta_arr = (c_float * self.mfit)()  # the gradient vector
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
            self.sig_ptr,  # standard dev
            self.yfit_ptr,  # model prediction
            c_int(self.ndata), # n data
            self.a_arr,  # initial params
            self.atry_arr,
            self.da_arr,
            self.beta_arr,
            c_int(self.ma), # n total params
            self.lista_arr, # parameter–index mapping array to keep track of which parameters are being fitted
            c_int(self.mfit), # n fitted params
            self.covar_mat,  # working space array
            self.alpha_mat,  # working space array
            self.oneda_mat,  # working space array
            byref(self.chisq),  # Pointer to current chi‑square value
            _________,  # FIXME: this should be the model function , e.g., the form factor
            byref(self.alamda),  # Levenberg–Marquardt control parameter
            c_int(self.error_type), # 0-4
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
    
    def cleanup(self):
        return
