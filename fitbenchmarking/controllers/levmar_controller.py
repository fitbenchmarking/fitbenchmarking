"""
Implements a controller for the levmar fitting software.
http://www.ics.forth.gr/~lourakis/levmar/
via the python interface
https://pypi.org/project/levmar/
"""

import numpy as np
import levmar

from fitbenchmarking.controllers.base_controller import Controller


class LevmarController(Controller):
    """
    Controller for the levmar fitting software
    """

    ALGORITHM_CHECK = {
            'all': ['levmar'],
            'ls': ['levmar'],
            'deriv_free': [],
            'general': [],
            'simplex': [],
            'trust_region': ['levmar'],
            'levenberg-marquardt': ['levmar'],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': []}

    def __init__(self, cost_func):
        """
        Initialise the class.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self.param_ranges = None
        self.lm_y = None
        self._popt = None
        self.algorithm_check = self.ALGORITHM_CHECK
        self._info = None

    def jacobian_information(self):
        """
        levmar can use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup problem ready to be run with levmar
        """

        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            lb = [None if x == -np.inf else x for x in lb]
            ub = [None if x == np.inf else x for x in ub]
            self.param_ranges = list(zip(lb, ub))
        self.lm_y = np.zeros(self.data_y.shape)

    def fit(self):
        """
        run problem with levmar
        """
        if self.problem.value_ranges is None:
            solve_levmar = getattr(levmar, "levmar")
        else:
            solve_levmar = getattr(levmar, "levmar_bc")
        args = [self.cost_func.eval_r,
                self.initial_params,
                self.lm_y]
        if self.value_ranges is not None:
            args.append(self.param_ranges)
        kwargs = {}
        if not self.jacobian.use_default_jac:
            kwargs["jacf"] = self.jacobian.eval
        (self.final_params, _, self._info) = solve_levmar(*args, **kwargs)
        # self._info isn't documented (other than in the levmar source),
        # but returns:
        # self._info[0] = ||e||_2 at `p0`
        # self._info[1] = ( ||e||_2 at `p`
        #                   ||J^T.e||_inf
        #                   ||Dp||_2
        #                   mu / max[J^T.J]_ii),
        # self._info[2] = number of iterations
        # self._info[3] = reason for terminating (as a string)
        # self._info[4] = number of `func` evaluations
        # self._info[5] = number of `jacf` evaluations
        # self._info[6] = number of linear system solved

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """

        if self._info[3] == "Stop by small Dp":
            self.flag = 0
        elif self._info[3] == "Stopped by small gradient J^T e":
            self.flag = 0
        elif self._info[3] == "Stopped by small ||e||_2":
            self.flag = 0
        elif self._info[3] == "maxit":
            self.flag = 1
        else:
            self.flag = 2
