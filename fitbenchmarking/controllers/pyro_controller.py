"""
Implements a controller for the Pyro software.
"""

import numpy as np
import torch
from pyro.infer import MCMC, NUTS

from fitbenchmarking.controllers.base_controller import Controller


class _NegLogLike(torch.autograd.Function):
    """
    Differentiable wrapper around the (numpy based) FitBenchmarking cost
    function, returning the negative log-likelihood and its gradient.
    """

    @staticmethod
    def forward(ctx, params, cost_func):
        p = params.detach().numpy()
        ctx.cost_func = cost_func
        ctx.save_for_backward(params)
        return torch.tensor(-cost_func.eval_loglike(p), dtype=params.dtype)

    @staticmethod
    def backward(ctx, grad_output):
        (params,) = ctx.saved_tensors
        # d/dp(-loglike) = d/dp(cost / 2)
        grad = 0.5 * np.asarray(
            ctx.cost_func.jac_cost(params.detach().numpy()), dtype=float
        )
        return grad_output * torch.from_numpy(grad).to(params.dtype), None


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

    support_for_bounds = False

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.mcmc = None
        self.warmup_steps = 300

    def _potential(self, inputs):
        """
        Potential energy (negative log-probability) used by NUTS.

        :param inputs: Dictionary containing the parameter tensor
        :type inputs: dict

        :return: The negative log-likelihood
        :rtype: torch.Tensor
        """
        return _NegLogLike.apply(inputs["params"], self.cost_func)

    def setup(self):
        """
        Setup problem ready to be run with Pyro
        """
        initial = {
            "params": torch.tensor(self.initial_params, dtype=torch.float64)
        }
        self.mcmc = MCMC(
            NUTS(potential_fn=self._potential),
            num_samples=self.chain_length,
            warmup_steps=self.warmup_steps,
            initial_params=initial,
            disable_progbar=True,
        )

    def fit(self):
        """
        Run problem with Pyro
        """
        self.mcmc.run()

    def cleanup(self):
        """
        Convert the samples to the posterior mean and populate the
        variables results will be read from
        """
        samples = self.mcmc.get_samples()["params"].numpy()

        self.params_pdfs = {
            name: samples[:, i].tolist()
            for i, name in enumerate(self.par_names)
        }
        self.final_params = samples.mean(axis=0).tolist()
        self.flag = 0
