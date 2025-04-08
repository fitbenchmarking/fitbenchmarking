"""
Implements a controller for the Mantid fitting software.
"""

from itertools import repeat
from typing import Union

import numpy as np
from mantid import simpleapi as msapi
from mantid.fitfunctions import FunctionFactory, IFunction1D

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import ControllerAttributeError


class MantidController(Controller):
    """
    Controller for the Mantid fitting software.

    Mantid requires subscribing a custom function in a predefined format,
    so this controller creates that in setup.
    """

    #: A map from fitbenchmarking cost functions to mantid ones.
    COST_FUNCTION_MAP = {
        "NLLSCostFunc": "Unweighted least squares",
        "WeightedNLLSCostFunc": "Least squares",
        "PoissonCostFunc": "Poisson",
        "LoglikeNLLSCostFunc": "Least squares",
    }

    algorithm_check = {
        "all": [
            "BFGS",
            "Conjugate gradient (Fletcher-Reeves imp.)",
            "Conjugate gradient (Polak-Ribiere imp.)",
            "Damped GaussNewton",
            "Levenberg-Marquardt",
            "Levenberg-MarquardtMD",
            "Simplex",
            "SteepestDescent",
            "Trust Region",
            "FABADA",
        ],
        "ls": ["Levenberg-Marquardt", "Levenberg-MarquardtMD", "Trust Region"],
        "deriv_free": ["Simplex"],
        "general": [
            "BFGS",
            "Conjugate gradient (Fletcher-Reeves imp.)",
            "Conjugate gradient (Polak-Ribiere imp.)",
            "Damped GaussNewton",
            "Simplex",
            "SteepestDescent",
        ],
        "simplex": ["Simplex"],
        "trust_region": [
            "Trust Region",
            "Levenberg-Marquardt",
            "Levenberg-MarquardtMD",
        ],
        "levenberg-marquardt": [
            "Levenberg-Marquardt",
            "Levenberg-MarquardtMD",
        ],
        "gauss_newton": ["Damped GaussNewton"],
        "bfgs": ["BFGS"],
        "conjugate_gradient": [
            "Conjugate gradient (Fletcher-Reeves imp.)",
            "Conjugate gradient (Polak-Ribiere imp.)",
        ],
        "steepest_descent": ["SteepestDescent"],
        "global_optimization": [],
        "MCMC": ["FABADA"],
    }

    jacobian_enabled_solvers = [
        "BFGS",
        "Conjugate gradient (Fletcher-Reeves imp.)",
        "Conjugate gradient (Polak-Ribiere imp.)",
        "Damped GaussNewton",
        "Levenberg-Marquardt",
        "Levenberg-MarquardtMD",
        "SteepestDescent",
        "Trust Region",
    ]

    support_for_bounds = True

    def __init__(self, cost_func):
        """
        Setup workspace, cost_function, ignore_invalid, and initialise vars
        used for temporary storage within the mantid controller

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        func_name = type(self.cost_func).__name__
        if func_name not in self.COST_FUNCTION_MAP:
            raise ControllerAttributeError(
                "Mantid Controller does not support"
                " the requested cost function "
                f"{func_name}"
            )
        self._cost_function = self.COST_FUNCTION_MAP[func_name]
        self._param_names = self.par_names

        # In case of mantid parser:
        #    mantid_equation is set in additional_info
        # In case of mantid dev parser:
        #    additional_info does not have the mantid_equation key
        self._mantid_equation = self.problem.additional_info.get(
            "mantid_equation", None
        )
        self._is_composite_function = (
            ";" in self._mantid_equation if self._mantid_equation else False
        )
        # dataset count > 1 if problem is multifit
        self._dataset_count = (
            len(self.data_x) if isinstance(self.data_x, list) else 1
        )

        if self.problem.multifit:
            # len(data_obj) will be equal to dataset count
            data_obj = [
                msapi.CreateWorkspace(
                    DataX=self.data_x[i],
                    DataY=self.data_y[i],
                    DataE=self.data_e[i],
                    OutputWorkspace=f"ws{i}",
                )
                for i in range(self._dataset_count)
            ]
            # _added_args are passed to the mantid function with
            # additional workspaces created for multifit data
            self._added_args = {
                f"InputWorkspace_{i + 1}": v
                for i, v in enumerate(data_obj[1:])
            }
        else:
            data_obj = msapi.CreateWorkspace(
                DataX=self.data_x, DataY=self.data_y, DataE=self.data_e
            )
            self._added_args = {}

        self._mantid_data = data_obj[0] if self.problem.multifit else data_obj
        self._status = None
        self._mantid_function = None
        self._mantid_results = None

    def _get_ties_str(self) -> str:
        """
        Returns the ties string for the problem. This is set in
        the function definition string passed to Mantid if the
        problem is multifit.

        :return: The string of ties.
        :rtype: str
        """
        return ",".join(
            f"f{i}.{p}=f0.{p}"
            for p in self.problem.additional_info["mantid_ties"]
            for i in range(1, self._dataset_count)
        )

    def _get_constraints_str(self) -> str:
        """
        Returns the constraints string for the problem. This is set in
        the function definition string passed to Mantid.

        :return: The string of constraints.
        :rtype: str
        """
        if self.problem.multifit:
            # Creates the constraint string for multifit problems.
            # For 3 parameters and 2 datasets the string will be:
            # 0.0 < f0.f0.A0 < 0.2,0.0 < f1.f0.A0 < 0.2,
            # 0.0 < f0.f1.A < 0.5,0.0 < f1.f1.A < 0.5,
            # 0.0 < f0.f1.Sigma < 0.05,0.0 < f1.f1.Sigma < 0.05
            return ",".join(
                f"{min} < f{j}.{p} < {max}"
                for (min, max), p in zip(self.value_ranges, self._param_names)
                for j in range(self._dataset_count)
            )
        else:
            if not self._is_composite_function:
                # When function is defined in the problem defination file as
                # 'name=LinearBackground,A0=0,A1=0', the param names are
                # prepended with f0.
                self._param_names = [
                    "f0." + name for name in self._param_names
                ]
            # Creates the constraint string for normal fitting.
            # For 3 parameters the string will be:
            # 0.0 < f0.A0 < 0.2,0.0 < f1.A < 0.5,0.0 < f1.Sigma < 0.05
            return ",".join(
                f"{min} < {name} < {max}"
                for (min, max), name in zip(
                    self.value_ranges, self._param_names
                )
            )

    def _setup_mantid(self) -> str:
        """
        Formats the mantid equation by setting the ties and constraints.
        This formated string is passed to the mantid fit function.

        :return: The updated function defination string.
        :rtype: str

        References
        ----------
        https://docs.mantidproject.org/nightly/fitting/fitfunctions/MultiDomainFunction.html
        """
        # Use the raw string format if this is from a Mantid problem.
        # This enables advanced features such as contraints.
        function_def = self._mantid_equation

        if self.problem.multifit:
            # Each function must include '$domains=i'
            if self._is_composite_function:
                function_def = (
                    " (composite=CompositeFunction, "
                    + "NumDeriv=false, $domains=i; "
                    + f"{function_def});"
                )
            else:
                function_def += ", $domains=i; "

            # Multifit must have 'composite=MultiDomainFunction' in the
            # first function.
            function_def = (
                "composite=MultiDomainFunction, NumDeriv=1;"
                + function_def * self._dataset_count
            )
            # Add the ties to the function definition
            function_def += f"ties=({self._get_ties_str()})"

        # Add constraints if parameter bounds are set
        if self.value_ranges is not None:
            function_def += f"; constraints=({self._get_constraints_str()})"

        return function_def

    def _setup_mantid_dev(self, return_class: bool = False) -> str:
        """
        Sets up a custom function to Mantid for calling in fit().
        This method is used when the mantid_equation is not set in
        additional_info.

        :param return_class: defaults to False, if True the fitFunction
                             class is returned for testing.
        :type return_class: boolean

        :return: The updated function defination string.
        :rtype: str
        """
        start_val_str = ", ".join(
            f"{name}={value}"
            for name, value in zip(self._param_names, self.initial_params)
        )
        function_def = "name=fitFunction, " + start_val_str

        class fitFunction(IFunction1D):
            """
            A wrapper to register a custom function in Mantid.

            References
            ----------
            https://docs.mantidproject.org/v6.9.1/tutorials/extending_mantid_with_python/advanced_fit_behaviours/02_analytical_derivatives.html
            """

            def init(ff_self):
                """
                Initialiser for the Mantid wrapper.
                """

                for i, p in enumerate(self._param_names):
                    ff_self.declareParameter(p)
                    if self.value_ranges is not None:
                        ff_self.addConstraints(
                            f"{self.value_ranges[i][0]}"
                            f" < {p} < "
                            f"{self.value_ranges[i][1]}"
                        )

            def function1D(ff_self, xdata):
                """
                Pass through for cost-function evaluation.
                """
                fit_param = np.array(
                    [ff_self.getParameterValue(p) for p in self._param_names]
                )
                return self.problem.eval_model(x=xdata, params=fit_param)

            if not self.cost_func.jacobian.use_default_jac:

                def functionDeriv1D(ff_self, xvals, jacobian):
                    """
                    Pass through for jacobian evaluation.
                    """
                    fit_param = np.array(
                        [
                            ff_self.getParameterValue(p)
                            for p in self._param_names
                        ]
                    )

                    jac = self.cost_func.jacobian.eval(fit_param)
                    for i, _ in enumerate(xvals):
                        for j in range(len(fit_param)):
                            jacobian.set(i, j, jac[i, j])

        FunctionFactory.subscribe(fitFunction)

        if return_class:
            # Returning the class for testing purposes
            return fitFunction
        return function_def

    def setup(self) -> None:
        """
        Setup problem ready to run with Mantid.
        """
        if self._mantid_equation is None:
            self._mantid_function = self._setup_mantid_dev()
        else:
            self._mantid_function = self._setup_mantid()

    def fit(self) -> None:
        """
        Run problem with Mantid.
        """
        if (minimizer_str := self.minimizer) == "FABADA":
            # The max iterations needs to be larger for FABADA
            # to work; setting to the value in the mantid docs
            minimizer_str += (
                f",Chain Length={self.chain_length}"
                ",Steps between values=10"
                ",Convergence Criteria=0.01"
                ",PDF=1,ConvergedChain=chain"
            )
            self._added_args["MaxIterations"] = 2000000

        fit_result = msapi.Fit(
            Function=self._mantid_function,
            CostFunction=self._cost_function,
            Minimizer=minimizer_str,
            InputWorkspace=self._mantid_data,
            Output="fit",
            **self._added_args,
        )

        self._mantid_results = fit_result
        self._status = self._mantid_results.OutputStatus

    def cleanup(self) -> None:
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == "success":
            self.flag = 0
        elif "Failed to converge" in self._status:
            self.flag = 1
        else:
            self.flag = 2

        final_params_dict = dict(
            zip(
                self._mantid_results.OutputParameters.column(0),
                self._mantid_results.OutputParameters.column(1),
            )
        )

        if self.minimizer == "FABADA":
            self.params_pdfs = {}
            n_chains = (
                self._mantid_results.ConvergedChain.getNumberHistograms()
            )
            for i in range(n_chains - 1):
                self.params_pdfs[self._param_names[i]] = (
                    self._mantid_results.ConvergedChain.readY(i).tolist()
                )

        if not self.problem.multifit:
            self.final_params = [
                final_params_dict[key] for key in self._param_names
            ]
        else:
            self.final_params = [
                [
                    final_params_dict[f"f{i}.{name}"]
                    for name in self._param_names
                ]
                for i in range(self._dataset_count)
            ]

    # Override if multi-fit
    # =====================
    def eval_chisq(
        self,
        params: Union[float, list[float]],
        x: Union[np.ndarray, list[np.ndarray], None] = None,
        y: Union[np.ndarray, list[np.ndarray], None] = None,
        e: Union[np.ndarray, list[np.ndarray], None] = None,
    ) -> Union[np.ndarray, list[np.ndarray]]:
        """
        Computes the chisq value.
        If multi-fit inputs will be lists and this will return a list of chi
        squared of params[i], x[i], y[i], and e[i].

        :param params: The parameters to calculate residuals for
        :type params: list of float or list of list of float
        :param x: x data points, defaults to self.data_x
        :type x: numpy array or list of numpy arrays, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array or list of numpy arrays, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array or list of numpy arrays, optional

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array or list of numpy arrays
        """
        if self.problem.multifit:
            x = x or list(repeat(None, len(params)))
            y = y or list(repeat(None, len(params)))
            e = e or list(repeat(None, len(params)))

            return [
                super(MantidController, self).eval_chisq(p, xi, yi, ei)
                for p, xi, yi, ei in zip(params, x, y, e)
            ]
        return super().eval_chisq(params, x, y, e)
