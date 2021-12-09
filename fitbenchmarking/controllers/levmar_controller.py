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

    algorithm_check = {
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

    jacobian_enabled_solvers = ['levmar']

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
        self._info = None

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
        if not self.cost_func.jacobian.use_default_jac:
            kwargs["jacf"] = self._jacobian_eval
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

    def _jacobian_eval(self, params, **kwargs):
        """
        A wrapper around the Jacobian eval function that makes sure the
        returned np array is contiguous in memory. Levmar is written in
        C/C++ and so will likely perform memory operations which can cause
        a bad fit if the Jacobian array is stored in non-contiguous memory.
        Note that non-contiguous memory can result from a transpose operation.

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: The computed Jacobian array in contiguous memory.
        :rtype: numpy array
        """
        return np.ascontiguousarray(self.cost_func.jac_res(params, **kwargs))

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
