"""
Implements a controller for the NLOPT software.
"""

import nlopt
import numpy as np
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError


class NLoptController(Controller):
    """
    Controller for NLOPT
    """

    algorithm_check = {
        'all': ['LN_BOBYQA',
                'LN_NEWUOA',
                'LN_NEWUOA_BOUND',
                'LN_PRAXIS',
                'LD_SLSQP',
                'LD_VAR2',
                'LD_VAR1',
                'AUGLAG',
                'AUGLAG_EQ',
                'LN_NELDERMEAD',
                'LN_SBPLX',
                'LN_COBYLA',
                'LD_CCSAQ',
                'LD_MMA',
                'LD_TNEWTON_PRECOND_RESTART',
                'LD_TNEWTON_PRECOND',
                'LD_TNEWTON_RESTART',
                'LD_TNEWTON',
                'LD_LBFGS',
                'GN_DIRECT',
                'GN_DIRECT_L',
                'GN_DIRECT_L_RAND',
                'GNL_DIRECT_NOSCAL',
                'GN_DIRECT_L_NOSCAL',
                'GN_DIRECT_L_RAND_NOSCAL',
                'GN_ORIG_DIRECT',
                'GN_ORIG_DIRECT_L',
                'GN_CRS2_LM',
                'G_MLSL_LDS',
                'G_MLSL',
                'GD_STOGO',
                'GD_STOGO_RAND',
                'GN_AGS',
                'GN_ISRES'],
        'ls': [],
        'deriv_free': ['LN_BOBYQA',
                       'LN_NEWUOA',
                       'LN_NEWUOA_BOUND',
                       'LN_PRAXIS'],
        'general': ['LD_SLSQP',
                    'LD_VAR2',
                    'LD_VAR1',
                    'AUGLAG',
                    'AUGLAG_EQ'],
        'simplex': ['LN_NELDERMEAD',
                    'LN_SBPLX'],
        'trust_region': ['LN_COBYLA',
                         'LD_CCSAQ',
                         'LD_MMA'],
        'levenberg-marquardt': [],
        'gauss_newton': ['LD_TNEWTON_PRECOND_RESTART',
                         'LD_TNEWTON_PRECOND',
                         'LD_TNEWTON_RESTART',
                         'LD_TNEWTON'],
        'bfgs': ['LD_LBFGS'],
        'conjugate_gradient': ['LN_COBYLA'],
        'steepest_descent': [],
        'global_optimization': ['GN_DIRECT',
                                'GN_DIRECT_L',
                                'GN_DIRECT_L_RAND',
                                'GNL_DIRECT_NOSCAL',
                                'GN_DIRECT_L_NOSCAL',
                                'GN_DIRECT_L_RAND_NOSCAL',
                                'GN_ORIG_DIRECT',
                                'GN_ORIG_DIRECT_L',
                                'GN_CRS2_LM',
                                'G_MLSL_LDS',
                                'G_MLSL',
                                'GD_STOGO',
                                'GD_STOGO_RAND',
                                'GN_AGS',
                                'GN_ISRES']}

    jacobian_enabled_solvers = ['LD_SLSQP',
                                'LD_VAR2',
                                'LD_VAR1',
                                'LD_CCSAQ',
                                'LD_MMA',
                                'LD_TNEWTON_PRECOND_RESTART',
                                'LD_TNEWTON_PRECOND',
                                'LD_TNEWTON_RESTART',
                                'LD_TNEWTON',
                                'GD_STOGO',
                                'GD_STOGO_RAND']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.support_for_bounds = True
        self.result = None
        self.opt = None
        self.value_ranges_ub = None
        self.value_ranges_lb = None
        self.bound_minimizers = self.algorithm_check['global_optimization'] + \
                                                    ['LN_NEWUOA_BOUND']
        self.local_optimizer_minimizers = ['G_MLSL',
                                           'G_MLSL_LDS',
                                           'GD_MLSL',
                                           'GD_MLSL_LDS',
                                           'AUGLAG',
                                           'AUGLAG_EQ']
        self._status = None

    def objective_master_nlopt(self, x, grad):
        """
        NLOPT objective function
        """

        jacs = self.cost_func.jac_cost(x)

        if grad.size > 0:
            np.copyto(grad, jacs)

        fx = self.cost_func.eval_cost(x)
        return fx

    def setup(self):
        """
        Setup problem ready to be run with NLOPT
        """

        nlopt_minimizer = getattr(nlopt, self.minimizer)
        self.opt = nlopt.opt(nlopt_minimizer, len(self.initial_params))

        if self.value_ranges is not None:
            self.value_ranges_lb, self.value_ranges_ub =  \
             zip(*self.value_ranges)
            self.opt.set_lower_bounds(list(self.value_ranges_lb))
            self.opt.set_upper_bounds(list(self.value_ranges_ub))

        if (self.value_ranges is None or np.any(np.isinf(self.value_ranges))) \
           and self.minimizer in self.bound_minimizers:
            raise MissingBoundsError(
                f"{self.minimizer} requires finite bounds on all"
                " parameters")

        if self.minimizer in self.local_optimizer_minimizers:
            local_opt = nlopt.opt(nlopt.LD_LBFGS, len(self.initial_params))
            self.opt.set_local_optimizer(local_opt)

        self.opt.set_min_objective(self.objective_master_nlopt)
        self.opt.set_maxeval(10000)

    def fit(self):
        """
        Run problem with NLOPT
        """

        self.result = self.opt.optimize(self.initial_params)
        self._status = self.opt.last_optimize_result()

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        converged = [nlopt.SUCCESS,
                     nlopt.XTOL_REACHED,
                     nlopt.FTOL_REACHED]

        if self._status in converged:
            self.flag = 0
        elif self._status == nlopt.MAXEVAL_REACHED:
            self.flag = 1
        else:
            self.flag = 2
        self.final_params = self.result
