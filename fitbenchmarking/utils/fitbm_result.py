"""
FitBenchmarking results object
"""

import numpy as np

# To store the results in the object requires more than the default
# max arguments and sanitised_name setter requires no use of self
# pylint: disable=too-many-arguments, no-self-use


class FittingResult:
    """
    Minimal definition of a class to hold results from a
    fitting problem test.
    """

    def __init__(self, options, cost_func, jac, hess, initial_params, params,
                 name=None, chi_sq=None, runtime=None, software=None,
                 minimizer=None, error_flag=None, dataset_id=None):
        """
        Initialise the Fitting Result

        :param options: Options used in fitting
        :type options: utils.options.Options
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        :param jac: The Jacobian definition
        :type jac: fitbenchmarking.jacobian.base_jacobian.Jacobian subclass
        :param hess: The Hessian definition
        :type hess: fitbenchmarking.hessian.base_hessian.Hessian subclass
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
        :param dataset_id: The index of the dataset (Only used for MultiFit),
                           defaults to None
        :type dataset_id: int, optional
        """
        self.options = options
        self.cost_func = cost_func
        self.problem = self.cost_func.problem
        self.jac = jac
        self.hess = hess
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
        self.costfun_tag = self.cost_func.__class__.__name__
        self.problem_tag = self.name
        self.software_tag = self.software
        self.minimizer_tag = self.minimizer
        self.jacobian_tag = self.jac.__class__.__name__
        self.hessian_tag = self.hess.__class__.__name__

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

    @property
    def sanitised_min_name(self):
        """
        Sanitise the minimizer name into one which can be used as a filename.

        :return: sanitised name
        :rtype: str
        """
        return self.minimizer.replace(':', '').replace(' ', '_')

    @sanitised_name.setter
    def sanitised_name(self, value):
        raise RuntimeError('sanitised_name can not be edited')

    @sanitised_min_name.setter
    def sanitised_min_name(self, value):
        raise RuntimeError('sanitised_min_name can not be edited')
