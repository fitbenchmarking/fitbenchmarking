"""
Implements a controller for the lmfit fitting software.
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
                'dual_annealing'],
        'ls': ['least_squares',
               'leastsq'],
        'deriv_free': ['powell',
                       'cobyla',
                       'nelder',
                       'differential_evolution'],
        'general': ['nelder',
                    'powell',
                    'cg',
                    'bfgs',
                    'newton',
                    'lbfgs',
                    'tnc',
                    'slsqp',
                    'differential_evolution',
                    'shgo',
                    'dual_annealing'],
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
        'conjugate_gradient': ['cg',
                               'newton',
                               'powell'],
        'steepest_descent': [],
        'global_optimization': ['differential_evolution',
                                'ampgo',
                                'shgo',
                                'dual_annealing'],
        'MCMC': ['emcee']
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
        self.support_for_bounds = True
        self.bound_minimizers = ['dual_annealing', 'differential_evolution']
        self.lmfit_out = None
        self.lmfit_params = Parameters()
        self._param_names = [
            f'p{i}' for (i, _) in enumerate(self.problem.param_names)]

    def lmfit_resdiuals(self, params):
        """
        lmfit resdiuals
        """
        return self.cost_func.eval_r(list(map(lambda name: params[name].value,
                                     self._param_names)))

    def lmfit_loglike(self, params):
        """
        lmfit resdiuals
        """
        return self.cost_func.eval_loglike(
            list(map(lambda name: params[name].value,
                     self._param_names))
        )

    def lmfit_jacobians(self, params):
        """
        lmfit jacobians
        """
        return self.cost_func.jac_cost(list(map(lambda name:
                                       params[name].value,
                                       self._param_names)))

    def setup(self):
        """
        Setup problem ready to be run with lmfit
        """

        if (self.value_ranges is None or np.any(np.isinf(self.value_ranges))) \
           and self.minimizer in self.bound_minimizers:
            raise MissingBoundsError(
                f"{self.minimizer} requires finite bounds on all"
                " parameters")

        for i, name in enumerate(self._param_names):
            kwargs = {"name": name,
                      "value": self.initial_params[i]}
            if self.value_ranges is not None:
                value_ranges_lb, value_ranges_ub =  \
                    zip(*self.value_ranges)
                kwargs["max"] = value_ranges_ub[i]
                kwargs["min"] = value_ranges_lb[i]
            self.lmfit_params.add(**kwargs)

    def fit(self):
        """
        Run problem with lmfit
        """
        kwargs = {"method": self.minimizer}
        if self.minimizer == "emcee":
            kwargs["progress"] = False
            kwargs["burn"] = 300
            minner = Minimizer(self.lmfit_loglike, self.lmfit_params)
        else:
            minner = Minimizer(self.lmfit_resdiuals, self.lmfit_params)

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

        self.iteration_count = self.lmfit_out.nfev
        self.count_type = 'function evaluations'

        if self.lmfit_out.success:
            self.flag = 0
        else:
            self.flag = 2

        if self.minimizer == 'emcee':
            params_pdf_dict = self.lmfit_out.flatchain.to_dict(orient='list')
            self.params_pdfs = dict(zip(self.problem.param_names,
                                        list(params_pdf_dict.values())))

        self.final_params = list(map(lambda params: params.value,
                                 self.lmfit_out.params.values()))
