"""
Implements a controller for the pyro software.
"""

import traceback

import torch
from pyro.infer import MCMC, NUTS

from fitbenchmarking.controllers.base_controller import Controller


class PyroController(Controller):
    """
    Controller for Pyro
    """

    algorithm_check = {
        "all": ["NUTS"],
        "ls": [],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": [],
        "levenberg-marquardt": [],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": ["NUTS"],
    }

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

    def loglike_eval(self, inputs):
        params = inputs["params"].tolist()
        return self.eval_loglike(params)

    def eval_r(self, params):
        return torch.tensor(self.cost_func.eval_r(params), requires_grad=True)

    def eval_loglike(self, params):
        return -1 / 2 * self.eval_cost(params)

    def eval_cost(self, params):
        r = self.eval_r(params)
        return torch.dot(r, r)

    def setup(self):
        """
        Setup problem ready to be run with Pyro
        """
        self.param_dict = {"params": torch.tensor(self.initial_params)}
        self.mcmc = MCMC(
            NUTS(potential_fn=self.loglike_eval),
            num_samples=10000,
            warmup_steps=300,
            initial_params=self.param_dict,
        )

    def fit(self):
        """
        Run problem with Paramonte
        """
        try:
            self.mcmc.run()
        except Exception:
            print(traceback.format_exc())

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        print(self.mcmc.get_samples())

        print(self.mcmc.summary())

        self.flag = 0
