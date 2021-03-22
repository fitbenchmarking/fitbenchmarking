"""
Implements a controller for the scipy ls fitting software.
In particular, for the scipy least_squares solver and minimizers
which support problems with parameter ranges.
"""

from scipy.optimize import least_squares
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class ScipyLSBoundsController(Controller):
    """
    Controller for the Scipy Least-Squares fitting software.
    """

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super(ScipyLSBoundsController, self).__init__(cost_func)
        self._param_names = self.problem.param_names
        self._popt = None
        self.algorithm_check = {
            'all': ['trf', 'dogbox'],
            'ls': ['trf', 'dogbox'],
            'deriv_free': [None],
            'general': [None]}

    def jacobian_information(self):
        """
        Scipy LS can use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup problem ready to be run with SciPy LS
        """
        # If parameter ranges have been set in problem, then set up bounds option for
        # scipy least_squares function. Here the bounds option must be a 2 tuple array
        # like object, the first tuple containing the lower bounds for each parameter
        # and the second containing all upper bounds.
        value_ranges_lb = []
        value_ranges_ub = []
        for name in self._param_names:
            if self.problem.value_ranges is not None and name in self.problem.value_ranges:
                value_ranges_lb.extend([self.problem.value_ranges[name][0]])
                value_ranges_ub.extend([self.problem.value_ranges[name][1]])
            else:
                value_ranges_lb.extend([-np.inf])
                value_ranges_ub.extend([np.inf])
        self.value_ranges = (value_ranges_lb, value_ranges_ub)

    def fit(self):
        """
        Run problem with Scipy LS.
        """
        self.result = least_squares(fun=self.cost_func.eval_r,
                                    x0=self.initial_params,
                                    method=self.minimizer,
                                    jac=self.jacobian.eval,
                                    bounds=self.value_ranges,
                                    max_nfev=500)

        self._popt = self.result.x
        self._status = self.result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status > 0:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._popt