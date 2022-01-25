"""
FitBenchmarking results object
"""

import numpy as np

from fitbenchmarking.utils.debug import get_printable_table


# pylint: disable=too-many-arguments, no-self-use
class FittingResult:
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options, cost_func, jac, hess, initial_params, params,
                 name=None, chi_sq=None, runtime=None, software=None,
                 minimizer=None, error_flag=None, algorithm_type=None,
                 dataset_id=None):
        """
        Initialise the Fitting Result

        :param options: Options used in fitting
        :type options: utils.options.Options
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        :param jac: The Jacobian used in the fitting
        :type jac: str
        :param hess: The Hessian used in the fitting
        :type hess: str
        :param initial_params: The starting parameters for the fit
        :type initial_params: list of float
        :param params: The parameters found by the fit
        :type params: list of float or list of list of float
        :param name: Name of the result, defaults to None
        :type name: str, optional
        :param chi_sq: The score for the fitting, defaults to None
        :type chi_sq: float or list of float, optional
        :param runtime: The average runtime of the fit, defaults to None
        :type runtime: float or list of float, optional
        :param software: The name of the software used, defaults to None
        :type software: str, optional
        :param minimizer: The name of the minimizer used, defaults to None
        :type minimizer: str, optional
        :param error_flag: [description], defaults to None
        :type error_flag: [type], optional
        :param algorithm_type: The tags associated with the minimizer,
                               defaults to None
        :type algorithm_type: str, optional
        :param dataset_id: The index of the dataset (Only used for MultiFit),
                           defaults to None
        :type dataset_id: int, optional
        """
        self.options = options
        self.cost_func = cost_func
        self.problem = self.cost_func.problem
        self.name = name if name is not None else \
            self.problem.name

        self.chi_sq = chi_sq
        if dataset_id is None:
            self.data_x = self.problem.data_x
            self.data_y = self.problem.data_y
            self.data_e = self.problem.data_e
            self.sorted_index = self.problem.sorted_index

            self.params = params
            self.chi_sq = chi_sq

        else:
            self.data_x = self.problem.data_x[dataset_id]
            self.data_y = self.problem.data_y[dataset_id]
            self.data_e = self.problem.data_e[dataset_id]
            self.sorted_index = self.problem.sorted_index[dataset_id]

            self.params = params[dataset_id]
            self.chi_sq = chi_sq[dataset_id]

        self.runtime = runtime

        self.min_chi_sq = None
        self.min_runtime = None

        # Minimizer for a certain problem and its function definition
        self.software = software
        self.minimizer = minimizer
        self.algorithm_type = algorithm_type
        self.jac = jac
        self.hess = hess

        # String interpretations of the params
        self.ini_function_params = self.problem.get_function_params(
            params=initial_params)
        self.fin_function_params = self.problem.get_function_params(
            params=self.params)

        # Controller error handling
        self.error_flag = error_flag

        # Paths to various output files
        self.problem_summary_page_link = ''
        self.fitting_report_link = ''
        self.start_figure_link = ''
        self.figure_link = ''

        # Error written to support page if plotting failed
        # Default can be overwritten with more information
        self.figure_error = 'Plotting Failed'

        self._norm_acc = None
        self._norm_runtime = None
        self.is_best_fit = False

        # Attributes for table creation
        self.costfun_tag: str = self.cost_func.__class__.__name__
        self.problem_tag: str = self.name
        self.software_tag: str = self.software \
            if self.software is not None else ""
        self.minimizer_tag: str = self.minimizer \
            if self.minimizer is not None else ""
        self.jacobian_tag: str = self.jac if self.jac is not None else ""
        self.hessian_tag: str = self.hess if self.hess is not None else ""

    def __str__(self):
        info = {"Cost Function": self.costfun_tag,
                "Problem": self.problem_tag,
                "Software": self.software_tag,
                "Minimizer": self.minimizer_tag,
                "Jacobian": self.jacobian_tag,
                "Hessian": self.hessian_tag,
                "Chi Squared": self.chi_sq,
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
            if self.min_chi_sq in [np.nan, np.inf]:
                self._norm_acc = np.inf
            else:
                self._norm_acc = self.chi_sq / self.min_chi_sq
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
