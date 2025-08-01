"""
FitBenchmarking results object
"""

from statistics import StatisticsError, fmean, harmonic_mean, median
from typing import TYPE_CHECKING, Literal, Optional, Union

import numpy as np
from scipy import stats

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.debug import get_printable_table
from fitbenchmarking.utils.log import get_logger

if TYPE_CHECKING:
    from fitbenchmarking.cost_func.base_cost_func import CostFunc
    from fitbenchmarking.parsing.fitting_problem import FittingProblem

LOGGER = get_logger()


class FittingResult:
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(
        self,
        controller: Controller,
        accuracy: Union[float, list[float]] = np.inf,
        runtimes: Union[float, list[float]] = np.inf,
        energy: float = np.inf,
        runtime_metric: Literal[
            "mean", "minimum", "maximum", "first", "median", "harmonic", "trim"
        ] = "mean",
        dataset: Optional[int] = None,
    ) -> None:
        """
        Initialise the Fitting Result

        :param controller: Controller used to fit
        :type controller: controller.base_controller.Controller
        :param accuracy: The score for the fitting, defaults to np.inf
        :type accuracy: Union[float, list[float]], optional
        :param runtimes: All runtimes of the fit, defaults to np.inf
        :type runtimes: Union[float, list[float]], optional
        :param energy: The average energy usage for the fit, defaults to np.inf
        :type energy: float, optional
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
        if hasattr(problem, "mask"):
            self.mask = problem.mask

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

        # Needed for spinw 2d case, for plotting
        indexes_cuts = None

        if "ebin_cens" in problem.additional_info:
            # If SpinW 1d, make sure data_x is correct
            if problem.additional_info["plot_type"] == "1d_cuts":
                n_plots = problem.additional_info["n_plots"]
                self.data_x = np.array(
                    n_plots * problem.additional_info["ebin_cens"].tolist()
                )

            # In the SpinW 2d case, produce cuts of data
            elif problem.additional_info["plot_type"] == "2d":
                n_plots = problem.additional_info["n_plots"]
                self.data_x_cuts = np.array(
                    n_plots * problem.additional_info["ebin_cens"].tolist()
                )
                indexes_cuts = self.get_indexes_1d_cuts_spinw(problem)
                self.data_y_cuts, self.data_y_complete = (
                    self.get_1d_cuts_spinw(problem, indexes_cuts, self.data_y)
                )

                if self.data_e is not None:
                    self.data_e_cuts, _ = self.get_1d_cuts_spinw(
                        problem, indexes_cuts, self.data_e
                    )

        self.runtimes = runtimes if isinstance(runtimes, list) else [runtimes]
        self.runtime_metric = runtime_metric
        self.energy = energy
        self.iteration_count = controller.iteration_count
        self.func_evals = controller.func_evals

        # Posterior pdfs for Bayesian fitting
        self.params_pdfs = controller.params_pdfs

        # Additional plotting info for SpinW powder plots
        if "n_plots" in problem.additional_info:
            self.plot_info = {
                "plot_type": problem.additional_info["plot_type"],
                "n_plots": problem.additional_info["n_plots"],
                "subplot_titles": problem.additional_info["subplot_titles"],
                "ax_titles": problem.additional_info["ax_titles"],
            }

            for key in ["modQ_cens", "ebin_cens"]:
                if key in problem.additional_info:
                    self.plot_info[key] = problem.additional_info[key].tolist()
        else:
            self.plot_info = None

        # Details of options used for this run
        self.software = controller.software
        self.minimizer = controller.minimizer
        self.algorithm_type = [
            k
            for k, v in controller.algorithm_check.items()
            if v == self.minimizer
        ]

        jac_enabled = (
            cost_func.jacobian is not None
            and self.minimizer in controller.jacobian_enabled_solvers
        )
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
        if hasattr(self, "ini_y") and indexes_cuts is not None:
            self.ini_y_cuts, _ = self.get_1d_cuts_spinw(
                problem, indexes_cuts, self.ini_y
            )

        self.fin_y = None
        if self.params is not None:
            cost_func.problem.timer.reset()
            if isinstance(cost_func, BaseNLLSCostFunc):
                self.r_x = cost_func.eval_r(
                    self.params, x=self.data_x, y=self.data_y, e=self.data_e
                )
                if hasattr(self, "r_x") and indexes_cuts is not None:
                    self.r_x_cuts, _ = self.get_1d_cuts_spinw(
                        problem, indexes_cuts, self.r_x
                    )
                self.jac_x = cost_func.jac_res(
                    self.params, x=self.data_x, y=self.data_y, e=self.data_e
                )
            self.fin_y = cost_func.problem.eval_model(
                self.params, x=self.data_x
            )
            if hasattr(self, "fin_y") and indexes_cuts is not None:
                self.fin_y_cuts, self.fin_y_complete = self.get_1d_cuts_spinw(
                    problem, indexes_cuts, self.fin_y
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

    def get_1d_cuts_spinw(self, problem, indexes, array_to_cut):
        """
        Given a flattened array of spinw y data, this function reshapes it
        into a 2d array (based on the length of ebin_cens), then takes
        1d cuts based on the q_cens specified by the user.
        """

        flattened_mask = self.mask.transpose().flatten()
        full_array = np.full(flattened_mask.shape, np.nan)
        full_array[~flattened_mask] = array_to_cut
        array_to_cut_as_2d = full_array.reshape(self.mask.shape, order="F")

        data_cuts = []
        for ind in indexes:
            if len(list(ind[0])) == 1:
                data_cuts = data_cuts + array_to_cut_as_2d[ind, :][0].tolist()

            elif len(list(ind[0])) > 1:
                mean_y = np.mean(array_to_cut_as_2d[ind, :][0], axis=0)
                data_cuts = data_cuts + mean_y.tolist()

        return data_cuts, array_to_cut_as_2d

    def get_indexes_1d_cuts_spinw(self, problem):
        """
        Get indexes of 1d cuts for SpinW data, based on the q_cens
        specified by the user.
        """
        modQ_cens = problem.additional_info["modQ_cens"]
        q_cens = problem.additional_info["q_cens"]
        dq = problem.additional_info["dq"]
        qmin = [float(i) - dq for i in q_cens]
        qmax = [float(i) + dq for i in q_cens]

        indexes_cuts = []
        for qmin_i, qmax_i in zip(qmin, qmax):
            indexes_cuts.append(
                np.where(
                    np.logical_and(modQ_cens >= qmin_i, modQ_cens <= qmax_i)
                )
            )
        return indexes_cuts

    def init_blank(self):
        """
        Initialise a new blank version of the class with the required
        placeholder values not set during standard initialisation.
        """
        # Variable for calculating best result
        self._norm_acc = None
        self._norm_energy = None
        self.min_accuracy = np.inf
        self.min_energy = np.inf
        self.is_best_fit = False

        self.min_mean_runtime = np.inf
        self.min_minimum_runtime = np.inf
        self.min_maximum_runtime = np.inf
        self.min_first_runtime = np.inf
        self.min_median_runtime = np.inf
        self.min_harmonic_runtime = np.inf
        self.min_trim_runtime = np.inf

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
            "Energy usage": self.energy,
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
        Getting function for minimum_runtime attribute

        :return: minimum_runtime value
        :rtype: float
        """
        return min(self.runtimes)

    @property
    def maximum_runtime(self):
        """
        Getting function for maximum_runtime attribute

        :return: maximum_runtime value
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
        # This try except is added to handle scenarios
        # when harmonic_mean cannot be calculated.
        try:
            return harmonic_mean(self.runtimes)
        except StatisticsError:
            return np.inf

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
            elif self.min_accuracy in [0.0, 0]:
                LOGGER.warning(
                    "The min accuracy of the dataset is 0. "
                    "The relative performance will be "
                    "approximated using a min of 1e-10."
                )
                self._norm_acc = self.accuracy / 1e-10
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

    def norm_runtime(self, runtime_metric=None):
        """
        Calculates the norm runtime of a given runtime metric.

        :return: normalised runtime value of the selected
        :rtype: float
        """
        metric = runtime_metric or self.runtime_metric
        min_rumtime = getattr(self, f"min_{metric}_runtime")
        if min_rumtime in [np.nan, np.inf]:
            norm_runtime = np.inf
        else:
            norm_runtime = getattr(self, f"{metric}_runtime") / min_rumtime
        return norm_runtime

    @property
    def norm_energy(self):
        """
        Getting function for norm_energy attribute

        :return: normalised energy value
        :rtype: float
        """
        if self._norm_energy is None:
            if self.min_energy in [np.nan, np.inf]:
                self._norm_energy = np.inf
            else:
                self._norm_energy = self.energy / self.min_energy
        return self._norm_energy

    @norm_energy.setter
    def norm_energy(self, value):
        """
        Stores the normalised energy and updates the value

        :param value: New value for norm_energy
        :type value: float
        """
        self._norm_energy = value

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
