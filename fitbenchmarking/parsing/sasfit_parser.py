"""
This file implements a parser for the SASFit data format.
"""

import ctypes
from ctypes import (
    CFUNCTYPE,
    POINTER,
    Structure,
    byref,
    c_bool,
    c_char,
    c_char_p,
    c_double,
    c_int,
    c_void_p,
    cast,
    pointer,
)

import numpy as np

from fitbenchmarking.parsing.fitbenchmark_parser import FitbenchmarkParser

# Not sure where the following should go, whether
# it should just be placed here before the parser

MAXPAR = 50
STRLEN = 256

FunctionType = CFUNCTYPE(c_double, c_double, c_void_p)


# Define the sasfit_param structure
class SASFIT_PARAM(Structure):
    _fields_ = [
        ("p", c_double * MAXPAR),
        ("kernelSelector", c_int),
        ("kernelSubSelector", c_int),
        ("errStr", c_char * STRLEN),
        ("errLen", c_int),
        ("errStatus", c_bool),
        ("xarr", c_void_p),
        ("yarr", c_void_p),
        ("moreparam", c_void_p),
        ("more_p", c_double * MAXPAR),
        ("function", FunctionType),
    ]


FunctionType2 = CFUNCTYPE(c_double, c_double, POINTER(SASFIT_PARAM))

SASFIT_FUNC_ONE_T = CFUNCTYPE(c_double, c_double, POINTER(SASFIT_PARAM))
SASFIT_FUNC_VOL_T = CFUNCTYPE(c_double, c_double, POINTER(SASFIT_PARAM), c_int)


class SASFIT_PLUGIN_FUNC_T(Structure):
    _fields_ = [
        ("len", c_int),
        ("name", c_char_p),
        ("func", POINTER(SASFIT_FUNC_ONE_T)),
        ("func_f", POINTER(SASFIT_FUNC_ONE_T)),
        ("func_v", POINTER(SASFIT_FUNC_VOL_T)),
    ]


class SASFIT_PLUGIN_INFO_T(Structure):
    _fields_ = [("num", c_int), ("functions", POINTER(SASFIT_PLUGIN_FUNC_T))]


class SASFIT_COMMON_STUBS_T(Structure):
    _fields_ = [
        ("func", c_void_p * 155),
    ]


class SASFitParser(FitbenchmarkParser):
    """
    Parser for a SASFit problem definition file.
    """

    def __init__(self):
        self.import_libraries()

    def parse(self, path_to_def_file):
        """
        This should be getting from a file:
        - the x values
        - the scattering function (for computing the expected y values)
        - the observed y values from real data (if we want to do the fitting)
        - the parameter values for sasfit_hankel and sasfit_integrate

        """

        # to add here once we know what a data file would look like
        # For now I'm just setting scattering function and x_data to something

        ff_g_dab_handle = self.sasfit_np.sasfit_ff_g_dab
        ff_g_dab_handle.argtypes = [c_double, POINTER(SASFIT_PARAM)]
        ff_g_dab_handle.restype = c_double

        py_values = [100.0, 0.5, 1.0, 1e-4]
        param_array = (c_double * MAXPAR)(*py_values)

        # Should be read as input from file but just setting these
        # like this for now
        self.scattering_fn = ff_g_dab_handle
        self.sasfit_params = param_array
        self.x_data = np.array([1.0, 2.0, 3.0])

    def import_libraries(self):
        """
        Any code needed for setting up interface to sasfit,
        mainly importing the libraries.
        Need to figure out what this should receive as input.

        """

        # NEEDS TO BE CHANGED
        base_path = "../SASfit/"
        self.sasfit = ctypes.CDLL(base_path + "libsasfit.so")
        self.sasfit_np = ctypes.CDLL(
            base_path + "plugins/libsasfit_non_particulate.so"
        )

        # Initialize plugins
        pi = (POINTER(SASFIT_PLUGIN_INFO_T) * 1)()
        self.sasfit.sasfit_common_stubs_ptr.restype = POINTER(
            SASFIT_COMMON_STUBS_T
        )

        # Call plugin init
        self.sasfit_np.do_init.restype = c_int
        self.sasfit_np.do_init(
            byref(pi),
            self.sasfit.sasfit_common_stubs_ptr(),
            self.sasfit.sasfit_plugin_search,
        )

    def compute_hankel_at_R(self, hankel_strategy, x):
        """
        NOT SURE THIS SHOULD BE HERE OR IN SOME OTHER FILE
        Computes sasfit_hankel at a certain x
        """
        hankel_transform_handle = self.sasfit.sasfit_hankel
        hankel_transform_handle.argtypes = [
            c_double,
            FunctionType,
            c_double,
            c_void_p,
        ]
        hankel_transform_handle.restype = c_double

        set_hankel_strategy = self.sasfit.sasfit_set_hankel_strategy
        set_hankel_strategy(c_int(hankel_strategy))

        # Wrapper around scattering_fn
        @FunctionType
        def gdab_t(q, params):
            t_param = cast(params, POINTER(SASFIT_PARAM))
            return self.scattering_fn(q, t_param)

        # Get sasfit_hankel
        nu = c_double(0.0)
        params = cast(pointer(self.sasfit_params), c_void_p)

        result_Gr = hankel_transform_handle(nu, gdab_t, np.abs(x), params)
        return result_Gr

    def compute_hankel_at_R0(self):
        """
        NOT SURE THIS SHOULD BE HERE OR IN SOME OTHER FILE
        Computes sasfit_integrate for x=0
        """

        # Wrapper 2 around scattering_fn
        @FunctionType2
        def gdab_hankel0(q, params):
            return q * self.scattering_fn(q, params)

        # Get sasfit_integrate
        params = cast(pointer(self.sasfit_params), POINTER(SASFIT_PARAM))
        sasfit_integrate_handle = self.sasfit.sasfit_integrate_ctm
        sasfit_integrate_handle.argtypes = [
            c_double,
            c_double,
            FunctionType2,
            POINTER(SASFIT_PARAM),
        ]
        sasfit_integrate_handle.restype = c_double

        result_G0 = sasfit_integrate_handle(0, np.inf, gdab_hankel0, params)
        return result_G0

    def compute_expected_y(self, hankel_strategy, x_data):
        """
        NOT SURE WHETHER THIS SHOULD GO HERE OR SOMEWHERE ELSE

        This should use the sasfit functions, specifically
        sasfit_hankel and sasfit_integrate to compute the expected
        y values using the formula (Gr-Go) / 2pi.

        Needs to receive:
        - the hankel strategy (AS INT)
        - the x values

        """
        G0 = self.compute_hankel_at_R0()

        for x in x_data:
            Gr = self.compute_hankel_at_Rt(hankel_strategy, x)

        res = (Gr - G0) / (2 * np.pi)
        return res
