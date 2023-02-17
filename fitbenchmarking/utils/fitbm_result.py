"""
FitBenchmarking results object
"""
from typing import TYPE_CHECKING

import numpy as np

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.debug import get_printable_table

if TYPE_CHECKING:
    from typing import Optional

    from fitbenchmarking.controllers.base_controller import Controller
    from fitbenchmarking.cost_func.base_cost_func import CostFunc
    from fitbenchmarking.parsing.fitting_problem import FittingProblem
    from fitbenchmarking.utils.options import Options


# pylint: disable=too-many-arguments, no-self-use
class FittingResult:
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self,
                 options: 'Options',
                 controller: 'Controller',
                 accuracy: 'float | list[float]' = np.inf,
                 runtime: 'float' = np.inf,
                 dataset: 'Optional[int]' = None) -> None:
        """
        Initialise the Fitting Result

        :param options: Options used in fitting
        :type options: utils.options.Options
        :param controller: Controller used to fit
        :type controller: controller.base_controller.Controller
        :param accuracy: The score for the fitting, defaults to np.inf
        :type accuracy: float | list[float], optional
        :param runtime: The average runtime of the fit, defaults to np.inf
        :type runtime: float | list[float], optional
        :param dataset: The index of the dataset (Only used for MultiFit),
                        defaults to None
        :type dataset: int, optional
        """
        self.init_blank()

        self.options: 'Options' = options
        cost_func: 'CostFunc' = controller.cost_func
        problem: 'FittingProblem' = controller.problem

        # Problem definition + scores
        self.name: 'str' = problem.name
        self.multivariate: 'bool' = problem.multivariate
        self.problem_format: 'str' = problem.format
        self.problem_desc: 'str' = problem.description
        self.initial_params: 'list[float]' = controller.initial_params
        self.equation = problem.equation

        if dataset is None:
            self.data_x = problem.data_x
            self.data_y = problem.data_y
            self.data_e = problem.data_e
            self.sorted_index = problem.sorted_index
            self.params = controller.final_params
            self.accuracy = accuracy
        else:
            self.name += f', Dataset {dataset + 1}'
            self.data_x = problem.data_x[dataset]
            self.data_y = problem.data_y[dataset]
            self.data_e = problem.data_e[dataset]
            self.sorted_index = problem.sorted_index[dataset]
            self.params = controller.final_params[dataset]
            self.accuracy = accuracy[dataset]

        self.runtime = runtime

        # Details of options used for this run
        self.software = controller.software
        self.minimizer = controller.minimizer
        self.algorithm_type = [k for k, v in controller.algorithm_check.items()
                               if v == self.minimizer]

        jac_enabled = self.minimizer in controller.jacobian_enabled_solvers
        hess_enabled = cost_func.hessian is not None \
            and self.minimizer in controller.hessian_enabled_solvers

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
                self.r_x = cost_func.eval_r(self.params,
                                            x=self.data_x,
                                            y=self.data_y,
                                            e=self.data_e)
                self.jac_x = cost_func.jac_res(self.params,
                                               x=self.data_x,
                                               y=self.data_y,
                                               e=self.data_e)
            self.fin_y = cost_func.problem.eval_model(
                self.params, x=self.data_x)

        # String interpretations of the params
        self.ini_function_params = problem.get_function_params(
            params=controller.initial_params)
        self.fin_function_params = problem.get_function_params(
            params=controller.final_params)

        # Controller error handling
        self.error_flag = controller.flag

        # Attributes for table creation
        self.costfun_tag: str = cost_func.__class__.__name__
        self.problem_tag: str = self.name
        self.software_tag: str = self.software \
            if self.software is not None else ""
        self.minimizer_tag: str = self.minimizer \
            if self.minimizer is not None else ""
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
        self.min_accuracy = np.inf
        self.min_runtime = np.inf
        self.is_best_fit = False

        # Paths to various output files
        self.problem_summary_page_link = ''
        self.fitting_report_link = ''
        self.start_figure_link = ''
        self.figure_link = ''
        self.figure_error = ''

    def __str__(self):
        info = {"Cost Function": self.costfun_tag,
                "Problem": self.problem_tag,
                "Software": self.software_tag,
                "Minimizer": self.minimizer_tag,
                "Jacobian": self.jacobian_tag,
                "Hessian": self.hessian_tag,
                "Accuracy": self.accuracy,
                "Runtime": self.runtime}

        return get_printable_table("FittingResult", info)

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
            name += f' [{self.software_tag}]'

        if self.jacobian_tag:
            name += f': j:{self.jacobian_tag}'

        if self.hessian_tag:
            name += f' h:{self.hessian_tag}'

        return name

    def sanitised_min_name(self, with_software=False):
        """
        Sanitise the modified minimizer name into one which can be used as a
        filename.

        :return: sanitised name
        :rtype: str
        """
        return self.modified_minimizer_name(with_software)\
            .replace(':', '').replace(' ', '_')

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

        :param value: New value for norm_runtime
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
    def sanitised_name(self):
        """
        Sanitise the problem name into one which can be used as a filename.

        :return: sanitised name
        :rtype: str
        """
        return self.name.replace(',', '').replace(' ', '_')

    @sanitised_name.setter
    def sanitised_name(self, value):
        raise RuntimeError('sanitised_name can not be edited')
