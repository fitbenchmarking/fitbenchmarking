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
from fitbenchmarking.cost_func.weighted_nlls_cost_func import (
    WeightedNLLSCostFunc,
)

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

    @property
    def has_errors(self) -> bool:
        """
        Whether the problem has errors to fit with.

        A multifit problem holds one array of errors per dataset, any of
        which may be missing.

        :return: True if every dataset has errors
        :rtype: bool
        """
        if self.data_e is None:
            return False
        if self.problem.multifit:
            return all(e is not None for e in self.data_e)
        return True

    def flatten(self, data):
        """
        Lay the datasets of a multifit problem end to end.

        The data of a multifit problem is held as one array per dataset,
        whereas the library fits a single run of points. The data of a
        single dataset problem is already in that form, so it is
        returned unchanged.

        :param data: The data to flatten
        :type data: numpy array, or list of numpy arrays

        :return: The data as one array
        :rtype: numpy array
        """
        return np.concatenate(data) if self.problem.multifit else data

    def setup(self):
        """
        Setup problem ready to be run
        """
        self.n_params = len(self.initial_params)
        self.n_fitted_params = len(self.initial_params)

        ############################################################
        # Setup the problem
        ############################################################

        # The library fits a single run of points, so the datasets of a
        # multifit problem are laid end to end. That is the order the
        # cost function returns the residuals of the combined parameters
        # in, so the model values and Jacobian rows line up with the data
        # without any reordering.
        self.ndata = self.residual_count

        # ---- Outputs ----
        # The library writes the fitted curve here, so it is held on the
        # controller rather than reached only through a raw pointer
        self.yfit_np = np.zeros(self.ndata, dtype=np.float32)
        self.chisq = c_float(0.0)

        # ---- Convert numpy arrays to c float* ----
        # The x values are not among these: the library only hands them
        # back to the model callback, which is given the indices below
        # instead, and the model is evaluated on the problem's own x
        self.data_y_np = np.asarray(
            self.flatten(self.data_y), dtype=np.float32, order="C"
        )

        # The library builds its residuals as (y - model) / sig, so 'sig'
        # is what carries the weighting. Only a weighted cost function
        # asks for the errors to be used, and even then the problem might
        # not have any, so everything else is fitted with unit errors.
        weighted = isinstance(self.cost_func, WeightedNLLSCostFunc)
        data_e = (
            self.flatten(self.data_e)
            if weighted and self.has_errors
            else np.ones(self.ndata)
        )
        self.data_e_np = np.asarray(data_e, dtype=np.float32, order="C")

        # The library passes each x value it is given straight back to
        # the model callback and does nothing else with it, so it is
        # given the index of each point in place of its x value. An x
        # value on its own does not say which point is being asked for:
        # a multifit problem repeats the same x grid once per dataset,
        # and a single dataset can measure the same x more than once.
        # A float holds indices below 2**24 exactly.
        self.point_index_np = np.arange(self.ndata, dtype=np.float32)

        self.index_ptr = self.point_index_np.ctypes.data_as(POINTER(c_float))
        self.y_ptr = self.data_y_np.ctypes.data_as(POINTER(c_float))
        self.sig_ptr = self.data_e_np.ctypes.data_as(POINTER(c_float))
        self.yfit_ptr = self.yfit_np.ctypes.data_as(POINTER(c_float))

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

        This is timed and so is run more than once for a single 'setup',
        which means everything the library changes as it goes has to be
        put back before starting.
        """
        for i, param in enumerate(self.initial_params):
            self.a_arr[i] = param
        # Negative to ask the library to do its own set up
        self.alamda = c_float(-1.0)
        self.chisq = c_float(0.0)
        self.error = c_bool(False)

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
            self.index_ptr,  # point indices, handed to the model function
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
        its derivatives at a single data point.

        The library asks for one data point at a time, but the model and
        its Jacobian are much cheaper to evaluate for the whole data set at
        once, so they are evaluated once per set of parameters and cached.
        The row needed by the current point is then picked out by index.

        For a multifit problem the model is evaluated from the combined
        parameters, which gives the values of every dataset laid end to
        end in the same order as the data, so the same indexing works.

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

            # The library is given the index of each point in place of
            # its x value, and hands back whatever it was given
            idx = round(x_i)

            if params != cache["params"]:
                cache["ymod"] = cost_func.problem.eval_model(
                    params, x=self.data_x
                )
                cache["jac"] = cost_func.jacobian.eval(params, x=self.data_x)
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
        """
        Copy a C array into a numpy array.

        The copy matters because the library keeps writing to its own
        arrays, so a view would carry on changing after it was read.

        :param ptr: The C array to copy
        :type ptr: ctypes array or pointer to c_float
        :param length: Number of values to copy
        :type length: int

        :return: The values, in double precision
        :rtype: numpy array
        """
        view = np.ctypeslib.as_array(ptr, shape=(length,))
        return np.array(view, dtype=np.float64)

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
