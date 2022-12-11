"""
Implements a controller for the Ceres fitting software.
"""
import numpy as np
from lmfit import Minimizer, Parameters
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError


class LmfitController(Controller):
    """
    Controller for lmfit
    """

    algorithm_check = {
        'all': ['differential_evolution',
                'powell',
                'cobyla',
                'slsqp',
                'emcee',
                'nelder',
                'least_squares',
                'trust-ncg',
                'trust-exact',
                'trust-krylov',
                'trust-constr',
                'dogleg',
                'leastsq',
                'newton',
                'tnc',
                'lbfgsb',
                'bfgs',
                'cg',
                'ampgo',
                'shgo',
                'dual_annealing'
                ],
        'ls': [],
        'deriv_free': ['powell',
                       'cobyla',
                       'slsqp',
                       'emcee',
                       ],
        'general': [],
        'simplex': ['nelder'],
        'trust_region': ['least_squares',
                         'trust-ncg',
                         'trust-exact',
                         'trust-krylov',
                         'trust-constr',
                         'dogleg'],
        'levenberg-marquardt': ['leastsq'],
        'gauss_newton': ['newton',
                         'tnc'],
        'bfgs': ['lbfgsb',
                 'bfgs'],
        'conjugate_gradient': ['cg'],
        'steepest_descent': [],
        'global_optimization': ['differential_evolution',
                                'ampgo',
                                'shgo',
                                'dual_annealing']
        }

    jacobian_enabled_solvers = ['cg',
                                'bfgs',
                                'newton',
                                'lbfgsb',
                                'tnc',
                                'slsqp',
                                'dogleg',
                                'trust-ncg',
                                'trust-krylov',
                                'trust-exact']

    hessian_enabled_solvers = ['newton',
                               'dogleg',
                               'trust-constr',
                               'trust-ncg',
                               'trust-krylov',
                               'trust-exact']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self._popt = None
        self.lmfit_out = None
        self.lmfit_p = None
        self.lmfit_params = Parameters()
        self.params_names = self.problem.param_names
        self.value_ranges_ub = None
        self.value_ranges_lb = None

    def lmfit_resdiuals(self, params):
        """
        lmfit resdiuals
        """
        self.lmfit_p = list(map(lambda name: params[name].value,
                            self.params_names))
        return self.cost_func.eval_r(self.lmfit_p)

    def lmfit_jacobians(self, params):
        """
        lmfit jacobians
        """
        self.lmfit_p = list(map(lambda name: params[name].value,
                            self.params_names))
        jac = self.cost_func.jac_res(self.lmfit_p)
        return jac[0]

    def setup(self):
        """
        Setup problem ready to be run with lmfit
        """

        if self.value_ranges is not None:
            self.value_ranges_lb, self.value_ranges_ub =  \
                zip(*self.value_ranges)

        if (self.value_ranges is None or np.any(np.isinf(self.value_ranges))) \
           and self.minimizer == 'differential_evolution':
            raise MissingBoundsError(
                    "Differential evolution' requires finite bounds on all"
                    " parameters")

        for i, name in enumerate(self.params_names):
            kwargs = {"name": name,
                      "value": self.initial_params[i]}
            if self.value_ranges_lb is not None \
               and self.value_ranges_ub is not None:
                kwargs["max"] = self.value_ranges_ub[i]
                kwargs["min"] = self.value_ranges_lb[i]
            self.lmfit_params.add(**kwargs)

    def fit(self):
        """
        Run problem with lmfit
        """

        minner = Minimizer(self.lmfit_resdiuals, self.lmfit_params)

        kwargs = {"method": self.minimizer}
        if self.minimizer in self.jacobian_enabled_solvers:
            kwargs["Dfun"] = self.lmfit_jacobians
        if self.cost_func.hessian and \
                self.minimizer in self.hessian_enabled_solvers:
            kwargs["hess"] = self.cost_func.hes_cost
        self.lmfit_out = minner.minimize(**kwargs)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        max_iters_messages = ['maximum number of iterations',
                              'iteration limit reached',
                              'iterations reached limit']

        if self.lmfit_out.success:
            self.flag = 0
        elif any(message in self.lmfit_out.message.lower()
                 for message in max_iters_messages):
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = list(map(lambda params: params.value,
                                 self.lmfit_out.params.values()))
