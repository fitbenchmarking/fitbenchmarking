"""
Implements the base class for the fitting software controllers.
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import curve_fit

from fitbenchmarking.utils.exceptions import (
    ControllerAttributeError,
    IncompatibleHessianError,
    IncompatibleJacobianError,
    IncompatibleMinimizerError,
    IncompatibleProblemError,
    MissingBoundsError,
    UnknownMinimizerError,
)

if TYPE_CHECKING:
    from fitbenchmarking.cost_func.base_cost_func import CostFunc


class Controller:
    """
    Base class for all fitting software controllers.
    These controllers are intended to be the only interface into the fitting
    software, and should do so by implementing the abstract classes defined
    here.
    """

    __metaclass__ = ABCMeta

    VALID_FLAGS = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    #: Within the controller class, you must
    #: initialize a dictionary, ``algorithm_check``,
    #: such that the **keys** are given by:
    #:
    #:     - ``all`` - all minimizers
    #:     - ``ls`` - least-squares fitting algorithms
    #:     - ``deriv_free`` - derivative free algorithms (these are algorithms
    #:       that cannot use information about derivatives -- e.g., the
    #:       ``Simplex`` method in ``Mantid``)
    #:     - ``general`` - minimizers which solve a generic `min f(x)`
    #:     - ``simplex`` - derivative free simplex based algorithms
    #:       e.g. Nelder-Mead
    #:     - ``trust_region`` - algorithms which emply a trust region approach
    #:     - ``levenberg-marquardt`` - minimizers that use the
    #:       Levenberg-Marquardt algorithm
    #:     - ``gauss_newton`` - minimizers that use the Gauss Newton algorithm
    #:     - ``bfgs`` - minimizers that use the BFGS algorithm
    #:     - ``conjugate_gradient`` - Conjugate Gradient algorithms
    #:     - ``steepest_descent`` - Steepest Descent algorithms
    #:     - ``global_optimization`` - Global Optimization algorithms
    #:     - ``MCMC`` - Markov Chain Monte Carlo algorithms
    #:
    #: The **values** of the dictionary are given as a list of minimizers
    #: for that specific controller that fit into each of the above
    #: categories. See for example the ``GSL`` controller.
    #:
    #: The ``algorithm_check`` dictionary is used to determine which minimizers
    #: to run given the ``algorithm_type`` selected in Fitting Options.
    #: For guidance on how to catagorise minimizers, see the Optimization
    #: Algorithms section of the FitBenchmarking docs.
    algorithm_check = {
        "all": [],
        "ls": [],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": [],
        "levenberg-marquardt": [],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    #: Within the controller class, you must define the list
    #: ``jacobian_enabled_solvers`` if any of the minimizers
    #: for the specific software are able to use jacobian
    #: information.
    #:
    #: - ``jacobian_enabled_solvers``: a list of minimizers in a
    #:   specific software that allow Jacobian information to
    #:   be passed into the fitting algorithm
    #:
    jacobian_enabled_solvers = []

    #: Within the controller class, you must define the list
    #: ``hessian_enabled_solvers`` if any of the minimizers
    #: for the specific software are able to use hessian
    #: information.
    #:
    #: - ``hessian_enabled_solvers``: a list of minimizers in a
    #:   specific software that allow Hessian information to
    #:   be passed into the fitting algorithm
    #:
    hessian_enabled_solvers = []

    #: Within the controller class, you must define the list
    #: ``sparsity`_enabled_solvers`` if any of the minimizers
    #: for the specific software offer support for sparse
    #: jacobians.
    #:
    #: - ``sparsity_enabled_solvers``: a list of minimizers in a
    #:   specific software that allow sparsity structure to be
    #:   passed into the fitting algorithm
    #:
    sparsity_enabled_solvers = []

    #: A name to be used in tables. If this is set to None it will be inferred
    #: from the class name.
    controller_name = None

    #: Used to check whether the fitting software has support for
    #: bounded problems, set as True if at least some minimizers
    #: in the fitting software have support for bounds
    support_for_bounds = False

    #: Used to check whether the selected minimizers is compatible with
    #: problems that have parameter bounds
    no_bounds_minimizers = []

    #: Used to check whether the selected minimizer is compatible with
    #: problems that don't have parameter bounds
    bounds_required_minimizers = []

    #: A list of incompatible problem formats for this controller.
    incompatible_problems = []

    def __init__(self, cost_func):
        """
        Initialise anything that is needed specifically for the
        software, do any work that can be done without knowledge of the
        minimizer to use, or function to fit, and call
        ``super(<software_name>Controller, self).__init__(problem)``
        (the base class's ``__init__`` implementation).

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        self.cost_func: CostFunc = cost_func
        # Problem: The problem object from parsing
        self.problem = self.cost_func.problem

        # Data: Data used in fitting. Might be different from problem
        #       if corrections are needed (e.g. startX)
        self.data_x = self.problem.data_x
        self.data_y = self.problem.data_y
        self.data_e = self.problem.data_e

        # Initial Params: The starting values for params when fitting
        self.initial_params = None
        # Staring Valuess: The list of starting parameters
        self.starting_values = self.problem.starting_values
        # Parameter Bounds: List of tuples of lower and upper bounds
        # for each parameter
        self.value_ranges = self.problem.value_ranges
        # Parameter set: The index of the starting parameters to use
        self.parameter_set = None
        # Minimizer: The current minimizer to use
        self.minimizer = None
        # Software: Use a property to get the name of the software from the
        # class
        self._software = ""

        # Final Params: The final values for the params from the minimizer
        self.final_params = None

        # Flag: error handling flag
        self._flag = None

        # The timer used to check if the 'max_runtime' is exceeded.
        self.timer = cost_func.problem.timer

        # save parameter estimates from MCMC minimizers
        self.params_pdfs = None

        self.par_names = self.problem.param_names

        # save iteration count
        self.iteration_count = None

        # save number of function evaluations
        self.func_evals = None

        # set default chain length for Bayesian minimizers
        self.chain_length = 100000

    @property
    def flag(self):
        """
        | 0: `Successfully converged`
        | 1: `Software reported maximum number of iterations exceeded`
        | 2: `Software run but didn't converge to solution`
        | 3: `Software raised an exception`
        | 4: `Solver doesn't support bounded problems`
        | 5: `Solution doesn't respect parameter bounds`
        | 6: `Solver has exceeded maximum allowed runtime`
        | 7: `Validation of the provided options failed`
        | 8: `Confidence in fit could not be calculated`
        """
        return self._flag

    @flag.setter
    def flag(self, value):
        if value not in self.VALID_FLAGS:
            raise ControllerAttributeError(
                "controller.flag must be one of "
                f"{list(self.VALID_FLAGS)}. Got: {value}."
            )
        self._flag = int(value)

    @property
    def software(self):
        """
        Return the name of the software.

        This assumes the class is named '<software>Controller'
        """
        if not self._software:
            if self.controller_name is not None:
                self._software = self.controller_name
            else:
                self._software = self.__class__.__name__[:-10].lower()
        return self._software

    def validate(self) -> None:
        """
        Validates that the provided options are compatible with each other.
        If there are some invalid options, the relevant exception is raised.
        """
        self._validate_jacobian()
        self._validate_hessian()
        self._validate_problem_format()

    def prepare(self, skip_setup=False):
        """
        Check that function and minimizer have been set.
        If both have been set, run self.setup().
        """

        if (self.minimizer is not None) and (self.parameter_set is not None):
            self.initial_params = list(
                self.starting_values[self.parameter_set].values()
            )

            if not skip_setup:
                self.setup()
        else:
            raise ControllerAttributeError(
                "Either minimizer or parameter_set is set to None."
            )

    def execute(self):
        """
        Starts and stops the timer used to check if the fit reaches
        the 'max_runtime'. In the middle, it calls self.fit().
        """
        self.timer.start()
        self.fit()
        self.timer.stop()

    def eval_chisq(self, params, x=None, y=None, e=None):
        """
        Computes the chisq value

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: x data points, defaults to self.data_x
        :type x: numpy array, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array, optional

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        kwargs = {k: v for k, v in zip("xye", [x, y, e]) if v is not None}
        out = self.cost_func.eval_cost(params=params, **kwargs)
        return out

    def eval_confidence(self):
        """
        Computes overall confidence in MCMC fit
        """
        self.params_pdfs["scipy_pfit"] = None
        self.params_pdfs["scipy_perr"] = None
        try:
            popt, pcov = curve_fit(
                self.problem.function,
                xdata=self.data_x,
                ydata=self.data_y,
                p0=self.initial_params,
                sigma=self.data_e,
            )

            perr = np.sqrt(np.diag(pcov))

            self.params_pdfs["scipy_pfit"] = popt.tolist()
            self.params_pdfs["scipy_perr"] = perr.tolist()

            # calculate overall confidence within 2 sigma tolerance
            par_conf = []
            for i, name in enumerate(self.par_names):
                tol = 2 * perr[i]
                hist, bin_edges = np.histogram(
                    self.params_pdfs[name.replace(".", "_")],
                    bins=100,
                    density=True,
                )
                # check tol range is covered by hist range
                tol_range = [popt[i] - tol, popt[i] + tol]
                if (
                    tol_range[-1] < bin_edges[0]
                    or tol_range[0] > bin_edges[-1]
                ):
                    par_conf.append(0)
                else:
                    width = np.diff(bin_edges)[0]
                    start_bin = np.argmin(abs(bin_edges - (popt[i] - tol)))
                    end_bin = np.argmin(abs(bin_edges - (popt[i] + tol)))
                    if start_bin == end_bin:
                        par_conf.append(hist[start_bin] * width)
                    else:
                        par_conf.append(sum(hist[start_bin:end_bin] * width))
        except RuntimeError as error_msg:
            par_conf = 0
            self.flag = 8
            print("\n" + str(error_msg))

        return np.prod(par_conf)

    def _validate_jacobian(self) -> None:
        """
        Validates that the provided Jacobian method is compatible with the
        other options and problem definition. An exception is raised if this
        is not true.
        """
        incompatible_problems = (
            self.cost_func.jacobian.INCOMPATIBLE_PROBLEMS.get(
                self.cost_func.jacobian.method, []
            )
        )

        if self.problem.format in incompatible_problems:
            message = (
                f"The {self.cost_func.jacobian.__class__.__name__} "
                f"Jacobian '{self.cost_func.jacobian.method}' "
                f"method is incompatible with the problem format "
                f"'{self.problem.format}'."
            )
            raise IncompatibleJacobianError(message)

    def _validate_hessian(self) -> None:
        """
        Validates that the provided Hessian method is compatible with the
        other options and problem definition. An exception is raised if this
        is not true.
        """
        if self.cost_func.hessian is not None:
            incompatible_problems = (
                self.cost_func.hessian.INCOMPATIBLE_PROBLEMS.get(
                    self.cost_func.hessian.method, []
                )
            )

            if self.problem.format in incompatible_problems:
                message = (
                    f"The {self.cost_func.hessian.__class__.__name__} "
                    f"Hessian '{self.cost_func.hessian.method}' "
                    f"method is incompatible with the problem format "
                    f"'{self.problem.format}'."
                )
                raise IncompatibleHessianError(message)

    def _validate_problem_format(self):
        """
        Validates that the problem format is compatible with the controller
        """
        if self.problem.format in self.incompatible_problems:
            raise IncompatibleProblemError(
                f"{self.problem.format} problems cannot be used with "
                f"{self.software} controllers."
            )

    def validate_minimizer(self, minimizer, algorithm_type):
        """
        Helper function which checks that the selected minimizer from the
        options (options.minimizer) exists and whether the minimizer is in
        self.algorithm_check[options.algorithm_type] (this is a list set in
        the controller)

        :param minimizer: string of minimizers selected from the
                          options
        :type minimizer: str
        :param algorithm_type: the algorithm type selected from the options
        :type algorithm_type: list
        """
        minimzer_selection = [[] for _ in range(len(algorithm_type))]

        for ind, alg in enumerate(algorithm_type):
            minimzer_selection[ind] = self.algorithm_check[alg]
        result = any(minimizer in list for list in minimzer_selection)

        if minimzer_selection == [[]]:
            message = (
                "For the selected software, there are no minimizers "
                "with the algorithm type(s) selected in the "
                "options file"
            )
            raise UnknownMinimizerError(message)

        if not result:
            message = (
                f"The algorithm type(s) of the minimizer selected,"
                f"{minimizer}, does not match the algorithm type(s)"
                "selected in the options file. For this software, "
                f"available minimizers are: {minimzer_selection}"
            )
            raise UnknownMinimizerError(message)

    def record_alg_type(self, minimizer, algorithm_type):
        """
        Helper function which records the algorithm types of
        the selected minimizer that match those chosen in options

        :param minimizer: string of minimizers selected from the
                          options
        :type minimizer: str
        :param algorithm_type: the algorithm type selected from the options
        :type algorithm_type: list
        """
        types = [
            k
            for k, v in self.algorithm_check.items()
            if minimizer in v and k in algorithm_type
        ]
        type_str = ", ".join(types)

        return type_str

    def check_minimizer_bounds(self, minimizer):
        """
        Helper function which checks whether the selected minimizer from the
        options (options.minimizer) supports problems with parameter bounds

        :param minimizer: string of minimizers selected from the
                          options
        :type minimizer: str
        """
        if self.value_ranges is not None and (
            self.support_for_bounds is False
            or minimizer in self.no_bounds_minimizers
        ):
            raise IncompatibleMinimizerError(
                "The selected minimizer does not currently support "
                "problems with parameter bounds"
            )

        if minimizer in self.bounds_required_minimizers and (
            self.value_ranges is None or np.any(np.isinf(self.value_ranges))
        ):
            raise MissingBoundsError(
                f"{minimizer} requires finite bounds on all parameters"
            )

    def check_bounds_respected(self):
        """
        Check whether the selected minimizer has respected
        parameter bounds
        """
        for count, value in enumerate(self.final_params):
            if (
                not self.value_ranges[count][0]
                <= value
                <= self.value_ranges[count][1]
            ):
                self.flag = 5

    def check_attributes(self):
        """
        A helper function which checks all required attributes are set
        in software controllers
        """
        values = {
            "_flag": int,
            "final_params": np.ndarray,
            "iteration_count": (int, type(None)),
            "func_evals": (int, type(None)),
        }

        for attr_name, attr_type in values.items():
            attr = getattr(self, attr_name)
            if attr_type != np.ndarray:
                if not isinstance(attr, attr_type):
                    raise ControllerAttributeError(
                        f"Attribute '{attr_name}' in the controller is not the"
                        f"expected type. Expected '{attr_type}', got "
                        f"{type(attr)}."
                    )
            else:
                # Mantid multifit produces final params as a list of final
                # params.
                if not self.problem.multifit:
                    attr = [attr]
                for a in attr:
                    if any(np.isnan(n) or np.isinf(n) for n in a):
                        raise ControllerAttributeError(
                            f"Attribute '{attr_name}' in the controller is "
                            "not the expected numpy ndarray of floats. "
                            "Expected a list or numpy ndarray of floats, got "
                            f"{attr}"
                        )

    @abstractmethod
    def setup(self):
        """
        Setup the specifics of the fitting.

        Anything needed for "fit" that can only be done after knowing the
        minimizer to use and the function to fit should be done here.
        Any variables needed should be saved to self (as class attributes).

        If a solver supports bounded problems, then this is where
        `value_ranges` should be set up for that specific solver. The default
        format is a list of tuples containing the lower and upper bounds
        for each parameter e.g. [(p1_lb, p2_ub), (p2_lb, p2_ub),...]
        """
        raise NotImplementedError

    @abstractmethod
    def fit(self):
        """
        Run the fitting.

        This will be timed so should include only what is needed
        to fit the data.
        """
        raise NotImplementedError

    @abstractmethod
    def cleanup(self):
        """
        Retrieve the result as a numpy array and store results.

        Convert the fitted parameters into a numpy array, saved to
        ``self.final_params``, and store the error flag as ``self.flag``.

        The flag corresponds to the following messages:

        .. automethod:: fitbenchmarking.controllers.base_controller.Controller.flag()
                :noindex:
        """  # noqa: E501
        raise NotImplementedError
