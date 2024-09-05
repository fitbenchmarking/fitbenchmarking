"""
FitBenchmarking results object
"""

from statistics import fmean, harmonic_mean, median
from typing import TYPE_CHECKING, Literal

import numpy as np
from scipy import stats

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.debug import get_printable_table

if TYPE_CHECKING:
    from typing import Optional

    from fitbenchmarking.controllers.base_controller import Controller
    from fitbenchmarking.cost_func.base_cost_func import CostFunc
    from fitbenchmarking.parsing.fitting_problem import FittingProblem


class FittingResult:
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(
        self,
        controller: "Controller",
        accuracy: "float | list[float]" = np.inf,
        runtimes: "float | list[float]" = np.inf,
        emissions: "float" = np.inf,
        runtime_metric: Literal[
            "mean", "minimum", "maximum", "first", "median", "harmonic", "trim"
        ] = "mean",
        dataset: "Optional[int]" = None,
    ) -> None:
        """
        Initialise the Fitting Result

        :param controller: Controller used to fit
        :type controller: controller.base_controller.Controller
        :param accuracy: The score for the fitting, defaults to np.inf
        :type accuracy: float | list[float], optional
        :param runtimes: All runtimes of the fit, defaults to np.inf
        :type runtimes: float | list[float], optional
        :param emissions: The average emissions for the fit, defaults to np.inf
        :type emissions: float | list[float], optional
        :param dataset: The index of the dataset (Only used for MultiFit),
                        defaults to None
        :type dataset: int, optional
        """
        self.init_blank()

        cost_func: CostFunc = controller.cost_func
        problem: FittingProblem = controller.problem

        # Problem definition + scores
        self.name: str = problem.name
        self.multivariate: bool = problem.multivariate
        self.problem_format: str = problem.format
        self.problem_desc: str = problem.description
        self.initial_params: list[float] = controller.initial_params
        self.param_names = controller.par_names
        self.equation = problem.equation
        self.plot_scale = problem.plot_scale

        if dataset is None:
            self.data_x = problem.data_x
            self.data_y = problem.data_y
            self.data_e = problem.data_e
            self.sorted_index = problem.sorted_index
            self.params = controller.final_params
            self.accuracy = accuracy
        else:
            self.name += f", Dataset {dataset + 1}"
            self.data_x = problem.data_x[dataset]
            self.data_y = problem.data_y[dataset]
            self.data_e = problem.data_e[dataset]
            self.sorted_index = problem.sorted_index[dataset]
            self.params = controller.final_params[dataset]
            self.accuracy = accuracy[dataset]

        self.runtimes = runtimes if isinstance(runtimes, list) else [runtimes]
        self.runtime_metric = runtime_metric
        self.emissions = emissions

        # Posterior pdfs for Bayesian fitting
        self.params_pdfs = controller.params_pdfs

        # Details of options used for this run
        self.software = controller.software
        self.minimizer = controller.minimizer
        self.algorithm_type = [
            k
            for k, v in controller.algorithm_check.items()
            if v == self.minimizer
        ]

        jac_enabled = self.minimizer in controller.jacobian_enabled_solvers
        hess_enabled = (
            cost_func.hessian is not None
            and self.minimizer in controller.hessian_enabled_solvers
        )

        self.jac = cost_func.jacobian.name() if jac_enabled else None
        self.hess = cost_func.hessian.name() if hess_enabled else None

        # Precalculate values required for plotting
        self.r_x = None
        self.jac_x = None

        self.ini_y = problem.ini_y(controller.parameter_set)
        self.fin_y = None
        if self.params is not None:
            cost_func.problem.timer.reset()
            if isinstance(cost_func, BaseNLLSCostFunc):
                self.r_x = cost_func.eval_r(
                    self.params, x=self.data_x, y=self.data_y, e=self.data_e
                )
                self.jac_x = cost_func.jac_res(
                    self.params, x=self.data_x, y=self.data_y, e=self.data_e
                )
            self.fin_y = cost_func.problem.eval_model(
                self.params, x=self.data_x
            )

        # String interpretations of the params
        self.ini_function_params = problem.get_function_params(
            params=controller.initial_params
        )
        self.fin_function_params = problem.get_function_params(
            params=controller.final_params
        )

        # Controller error handling
        self.error_flag = controller.flag

        # Attributes for table creation
        self.costfun_tag: str = cost_func.__class__.__name__
        self.problem_tag: str = self.name
        self.software_tag: str = (
            self.software if self.software is not None else ""
        )
        self.minimizer_tag: str = (
            self.minimizer if self.minimizer is not None else ""
        )
        self.jacobian_tag: str = self.jac if self.jac is not None else ""
        self.hessian_tag: str = self.hess if self.hess is not None else ""

    def init_blank(self):
        """
        Initialise a new blank version of the class with the required
        placeholder values not set during standard initialisation.
        """
        # Variable for calculating best result
        self._norm_acc = None
        self._norm_runtime = None
        self._norm_emissions = None
        self.min_accuracy = np.inf
        self.min_runtime = np.inf
        self.min_emissions = np.inf
        self.is_best_fit = False

        # Paths to various output files
        self.problem_summary_page_link = ""
        self.fitting_report_link = ""
        self.start_figure_link = ""
        self.figure_link = ""
        self.figure_error = ""
        self.posterior_plots = ""

    def __str__(self):
        info = {
            "Cost Function": self.costfun_tag,
            "Problem": self.problem_tag,
            "Software": self.software_tag,
            "Minimizer": self.minimizer_tag,
            "Jacobian": self.jacobian_tag,
            "Hessian": self.hessian_tag,
            "Accuracy": self.accuracy,
            "Runtime": self.runtime,
            "Runtime metric": self.runtime_metric,
            "Runtimes": self.runtimes,
            "Emissions": self.emissions,
        }

        return get_printable_table("FittingResult", info)

    def __eq__(self, other):
        for key in self.__dict__:
            if hasattr(other, key):
                match = getattr(other, key) != getattr(self, key)
                if not isinstance(match, bool):
                    match = (getattr(other, key) != getattr(self, key)).all()
                if match:
                    print(f"{key} not equal!")
                    return False
            else:
                print(f"No attr {key}")
                return False
        return True

    def get_n_parameters(self):
        """
        Returns number of parameters for the result.

        :return: Number of parameters
        :rtype: Int
        """
        return len(self.initial_params)

    def get_n_data_points(self):
        """
        Returns number of data points for the result.

        :return: Number of data points
        :rtype: Int
        """
        return len(self.data_x)

    def modified_minimizer_name(self, with_software: bool = False) -> str:
        """
        Get a minimizer name which contains jacobian and hessian information.
        Optionally also include the software.

        :param with_software: Add software to the name, defaults to False
        :type with_software: bool, optional
        :return: A name for the result combination
        :rtype: str
        """
        name: str = self.minimizer_tag
        if with_software:
            name += f" [{self.software_tag}]"

        if self.jacobian_tag:
            name += f": j:{self.jacobian_tag}"

        if self.hessian_tag:
            name += f" h:{self.hessian_tag}"

        return name

    def sanitised_min_name(self, with_software=False):
        """
        Sanitise the modified minimizer name into one which can be used as a
        filename.

        :return: sanitised name
        :rtype: str
        """
        return (
            self.modified_minimizer_name(with_software)
            .replace(":", "")
            .replace(" ", "_")
        )

    @property
    def runtime_metric(self):
        """
        Getting function for runtime_metric attribute

        :return: runtime_metric value
        :rtype: str
        """
        return self._runtime_metric

    @runtime_metric.setter
    def runtime_metric(self, value):
        """
        Stores the runtime_metric

        :param value: New value for runtime_metric
        :type value: str
        """
        self._runtime_metric = value
        self.runtime = getattr(self, value + "_runtime")

    @property
    def mean_runtime(self):
        """
        Getting function for mean_runtime attribute

        :return: mean_runtime value
        :rtype: float
        """
        return fmean(self.runtimes)

    @property
    def minimum_runtime(self):
        """
        Getting function for min_runtime attribute

        :return: min_runtime value
        :rtype: float
        """
        return min(self.runtimes)

    @property
    def maximum_runtime(self):
        """
        Getting function for max_runtime attribute

        :return: max_runtime value
        :rtype: float
        """
        return max(self.runtimes)

    @property
    def first_runtime(self):
        """
        Getting function for first_runtime attribute

        :return: first_runtime value
        :rtype: float
        """
        return self.runtimes[0]

    @property
    def median_runtime(self):
        """
        Getting function for meadian_runtime attribute

        :return: median_runtime value
        :rtype: float
        """
        return median(self.runtimes)

    @property
    def harmonic_runtime(self):
        """
        Getting function for harmonic_runtime attribute

        :return: harmonic_runtime value
        :rtype: float
        """
        return harmonic_mean(self.runtimes)

    @property
    def trim_runtime(self):
        """
        Getting function for trimmed_runtime attribute

        :return: trimmed_runtime value
        :rtype: float
        """
        return stats.trim_mean(self.runtimes, 0.2)

    @property
    def norm_acc(self):
        """
        Getting function for norm_acc attribute

        :return: normalised accuracy value
        :rtype: float
        """
        if self._norm_acc is None:
            if self.min_accuracy in [np.nan, np.inf]:
                self._norm_acc = np.inf
            else:
                self._norm_acc = self.accuracy / self.min_accuracy
        return self._norm_acc

    @norm_acc.setter
    def norm_acc(self, value):
        """
        Stores the normalised accuracy and updates the value

        :param value: New value for norm_accuracy
        :type value: float
        """
        self._norm_acc = value

    @property
    def norm_runtime(self):
        """
        Getting function for norm_runtime attribute

        :return: normalised runtime value
        :rtype: float
        """
        if self._norm_runtime is None:
            if self.min_runtime in [np.nan, np.inf]:
                self._norm_runtime = np.inf
            else:
                self._norm_runtime = self.runtime / self.min_runtime
        return self._norm_runtime

    @norm_runtime.setter
    def norm_runtime(self, value):
        """
        Stores the normalised runtime and updates the value

        :param value: New value for norm_runtime
        :type value: float
        """
        self._norm_runtime = value

    @property
    def norm_emissions(self):
        """
        Getting function for norm_emissions attribute

        :return: normalised emissions value
        :rtype: float
        """
        if self._norm_emissions is None:
            if self.min_emissions in [np.nan, np.inf]:
                self._norm_emissions = np.inf
            else:
                self._norm_emissions = self.emissions / self.min_emissions
        return self._norm_emissions

    @norm_emissions.setter
    def norm_emissions(self, value):
        """
        Stores the normalised emissions and updates the value

        :param value: New value for norm_emissions
        :type value: float
        """
        self._norm_emissions = value

    @property
    def sanitised_name(self):
        """
        Sanitise the problem name into one which can be used as a filename.

        :return: sanitised name
        :rtype: str
        """
        return self.name.replace(",", "").replace(" ", "_")

    @sanitised_name.setter
    def sanitised_name(self, value):
        raise RuntimeError("sanitised_name can not be edited")
