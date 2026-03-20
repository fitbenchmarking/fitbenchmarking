"""
Implements a controller for SASFit
"""
import numpy as np
import ctypes as ct
from ctypes import (
    c_int, c_float, c_bool, POINTER, Structure, CFUNCTYPE, byref, pointer, cast
)

from fitbenchmarking.controllers.base_controller import Controller


class sasfit_analytpar(Structure):
    _fields_ = []  # Probably okay to stay empty

class SASFIT_CData(Structure):
    _fields_ = [
        ("alpha", POINTER(POINTER(c_float))),
        ("covar", POINTER(POINTER(c_float))),
        ("oneda", POINTER(POINTER(c_float))),
        ("beta",  POINTER(c_float)),
        ("a",     POINTER(c_float)),
        ("da",    POINTER(c_float)),
        ("atry",  POINTER(c_float)),
        ("lista", POINTER(c_int)),
        ("ma",    c_int),
        ("mfit",  c_int),
        ("max_SD",c_int),
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
            None,
            c_float,                  # x_i
            c_float,                  # res_i
            POINTER(c_float),         # a
            POINTER(c_float),         # ymod
            POINTER(c_float),         # ysub
            POINTER(c_float),         # dyda
            c_int,                    # max_SD
            POINTER(sasfit_analytpar),# AP
            c_int,                    # error_type
            c_int,                    # flag
            POINTER(c_bool)           # error
        )

        # ---- Bind the C functions ----
        self.lib.SASFITmrqmin.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),  # x,y,sig,res
            POINTER(c_float), POINTER(c_float),                                      # yfit, ysubstr
            c_int, c_int,                                                            # ndata, max_SD
            POINTER(sasfit_analytpar), c_int,                                        # AP, error_type
            POINTER(SASFIT_CData),                                                   # SASFIT_CData[]
            POINTER(c_float),                                                        # chisq
            FUNCS_T,                                                                 # funcs
            POINTER(c_float),                                                        # alamda
            POINTER(c_bool)                                                          # error
        ]
        self.lib.SASFITmrqmin.restype = None

        self.lib.SASFITmrqcof.argtypes = [
            POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float),
            POINTER(c_float), POINTER(c_float), c_int,
            POINTER(c_float), POINTER(c_int), c_int, c_int,
            POINTER(sasfit_analytpar), c_int, c_int,
            POINTER(POINTER(c_float)), POINTER(c_float), POINTER(c_float),
            FUNCS_T, POINTER(c_bool)
        ]
        self.lib.SASFITmrqcof.restype = None

        self.lib.SASFITgaussj.argtypes = [POINTER(POINTER(c_float)), c_int, POINTER(POINTER(c_float)), c_int, POINTER(c_bool)]
        self.lib.SASFITgaussj.restype = None

        self.lib.SASFITcovsrt.argtypes = [POINTER(POINTER(c_float)), c_int, POINTER(c_int), c_int, POINTER(c_bool)]
        self.lib.SASFITcovsrt.restype = None

        ############################################################
        # Setup the problem
        ############################################################

        self.ndata = len(self.data_x)

        # outputs
        yfit_np    = np.zeros(self.ndata, dtype=np.float32)
        ysubstr_np = np.zeros(self.ndata, dtype=np.float32)
        ysubstr_np = np.zeros(self.ndata, dtype=np.float32)
        res_np = np.zeros(self.ndata, dtype=np.float32)
        self.chisq = c_float(0.0)

        # ---- Convert numpy arrays to c float* ----
        self.x_ptr   = self.data_x.ctypes.data_as(POINTER(c_float))
        self.y_ptr   = self.data_y.ctypes.data_as(POINTER(c_float))
        self.sig_ptr = ??? .ctypes.data_as(POINTER(c_float))               # FIXME: Do we read sigma in ??
        self.res_ptr = res_np.ctypes.data_as(POINTER(c_float))
        self.yfit_ptr    = yfit_np.ctypes.data_as(POINTER(c_float))
        self.ysubstr_ptr = ysubstr_np.ctypes.data_as(POINTER(c_float))

        # ---- Other inputs for fitting ----
        # FIXME: below params are required to reun the fit, but no clue whether we 
        # can read them in from initial_params
        # ma and mfit are n parameters and n fitted
        # defining some dummy here for simplicity
        ma = c_int(self.initial_params['n_params'])                 # n params  # FIXME: determine using len
        mfit = c_int(self.initial_params['n_fitted_params'])        # n fitted
        self.max_SD = c_int(self.initial_params['max_SD'])          # Maximum number of "size distribution" parameters
        self.alamda = c_float(self.initial_params['alamda'])        # Levenberg–Marquardt control parameter
        self.error_type = c_int(self.initial_params['error_type'])  # this is 0-4 for linera, log, sqrt, poisson-like

        # ---- LM parameter arrays ----
        a_arr    = (c_float * ma)(* [1.0, 1.0])  # initial guess        # FIXME: Substitute with intial params
        da_arr   = (c_float * ma)()
        atry_arr = (c_float * ma)()
        beta_arr = (c_float * mfit)()
        lista_arr = (c_int * mfit)(*list(range(mfit)))  # fit both parameters

        # ---- Matrices: alpha, covar (mfit x mfit), oneda (mfit x 1) ----
        alpha_mat, _ = self.make_matrix_float(mfit, mfit)
        covar_mat, _ = self.make_matrix_float(mfit, mfit)
        oneda_mat, _ = self.make_matrix_float(mfit, 1)

        cdata = SASFIT_CData(
            alpha_mat, covar_mat, oneda_mat,
            beta_arr,
            a_arr, da_arr, atry_arr,
            lista_arr,
            ma, mfit, self.max_SD, 
            c_float(0.0)
        )

        self.cdata_array = (SASFIT_CData * 1)(cdata)


    def fit(self):
        """
        Run problem 
        """
        self.lib.SASFITmrqmin(
            self.x_ptr,    # x values
            self.y_ptr,    # measured y
            self.sig_ptr,  # signma values
            self.res_ptr,  # residuals
            self.yfit_ptr, # model prediction
            self.ysubstr_ptr,  # A second model component to subtract before fitting. Used in SASFIT for background subtraction.
            self.ndata,    # Number of data points.
            self.max_SD,   # Maximum number of "size distribution" parameters
            byref(sasfit_analytpar()),     
            self.error_type,    # this is 0-4 for linera, log, sqrt, poisson-like
            self.cdata_array,    # struct containing all working memory for the LM fit
            byref(self.chisq),   # Pointer to current chi‑square value
            funcs,          # Callback for evaluating the model , this is the func evaluating the model - FIXME: is this passed in?
            byref(self.alamda),  # The Levenberg–Marquardt control parameter:
            byref(c_bool(False))      # Set to TRUE if anything goes wrong
        )


    def make_matrix_float(self, rows, cols):
        """
        Helper to create float** matrices
        Returns (mat_ptr, row_buffers) where:
        - mat_ptr is POINTER(POINTER(c_float)) suitable for passing to C as float** 
        - row_buffers is a list you must KEEP referenced so memory isn't GC'd
        """
        RowArray = (c_float * cols)
        row_buffers = [RowArray() for _ in range(rows)]
        # Build array of row pointers
        MatArray = POINTER(c_float) * rows
        mat = MatArray(*[row_buffers[r] for r in range(rows)])
        return mat, row_buffers
    