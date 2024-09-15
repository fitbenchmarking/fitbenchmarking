"""
Implements a controller for the Theseus fitting software.
"""

from typing import List, Optional, Sequence, Tuple

import numpy as np
import theseus as th
import torch

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class TheseusCostFunction(th.CostFunction):
    """
    Cost function for Theseus ai
    """

    def __init__(
        self,
        fb_cf,
        var: List[th.Vector],
        auxvar: Sequence[th.Variable],
        dim: int,
        cost_weight: Optional[th.CostWeight] = None,
        name: Optional[str] = None,
    ):
        if cost_weight is None:
            cost_weight = th.ScaleCostWeight(1.0)

        super().__init__(cost_weight, name=name)
        self.fb_cf = fb_cf
        self.var = var
        self.auxvar = auxvar or []
        self._dim = dim

        if len(var) < 1:
            raise ValueError(
                "TheseusCostFunction must receive at least one optimization variable."
            )

        self.register_vars(var, is_optim_vars=True)
        self.register_vars(auxvar, is_optim_vars=False)

    def error(self) -> Tuple[List[torch.Tensor], List[float]]:
        """
        Resdiuals in pytorch tensor form for Theseus ai
        """

        optim_vars_list = [float(optim_vars1[0]) for optim_vars1 in self.optim_vars]
        res = self.fb_cf.eval_r(optim_vars_list)
        th_res = torch.Tensor(np.array([res]))
        return th_res

    def jacobians(self) -> Tuple[List[torch.Tensor], torch.Tensor]:
        """
        Jacobians in pytorch tensor form for Theseus ai
        """

        err = self.error()
        optim_vars_list = [float(optim_vars1[0]) for optim_vars1 in self.optim_vars]
        jacs = self.fb_cf.jac_res(optim_vars_list)
        th_jac = [
            torch.Tensor([[[item] for item in jacs[:, index]]])
            for index in range(len(optim_vars_list))
        ]
        return th_jac, err

    def dim(self) -> int:
        """
        Lenght of x data
        """
        return self._dim

    def _copy_impl(self, new_name: Optional[str] = None):
        return TheseusCostFunction(  # type: ignore
            var=[v.copy() for v in self.var],
            auxvar=[v.copy() for v in self.auxvar],
            cost_weight=self.weight.copy(),
            name=new_name,
            fb_cf=self.fb_cf,
            dim=self._dim,
        )


class TheseusController(Controller):
    """
    Controller for Theseus
    """

    algorithm_check = {
        "all": ["Levenberg_Marquardt", "Gauss-Newton"],
        "ls": ["Levenberg_Marquardt", "Gauss-Newton"],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": [],
        "levenberg-marquardt": ["Levenberg_Marquardt"],
        "gauss_newton": ["Gauss-Newton"],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = ["Levenberg_Marquardt", "Gauss-Newton"]

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self._status = None
        self.th_objective = None
        self.th_optim = None
        self.th_info = None
        self.th_cost_func = None
        self._param_names = self.problem.param_names
        self.th_inputs = None
        self.result = None

    def setup(self):
        """
        Setup problem ready to be run with Theseus
        """
        x_tensor = torch.from_numpy(np.array([self.problem.data_x]))
        y_tensor = torch.from_numpy(np.array([self.problem.data_y]))

        th_x = th.Variable(x_tensor.float(), name="x_data")
        th_y = th.Variable(y_tensor.float(), name="y_data")

        th_aux_vars = th_x, th_y
        th_optim_vars = [th.Vector(1, name=f"{name}") for name in self._param_names]

        params = [params * torch.ones((1, 1)) for params in self.initial_params]
        param_dict = dict(zip(self.problem.param_names, params))

        self.th_inputs = {"x_data": th_x, "y_data": th_y, **param_dict}

        self.th_objective = th.Objective()

        self.th_cost_func = TheseusCostFunction(
            self.cost_func,
            th_optim_vars,
            th_aux_vars,
            name="theseus",
            dim=len(self.data_x),
        )

        self.th_objective.add(self.th_cost_func)

        if self.minimizer == "Levenberg_Marquardt":
            optimizer = th.LevenbergMarquardt(self.th_objective, max_iterations=100000)

        elif self.minimizer == "Gauss-Newton":
            optimizer = th.GaussNewton(self.th_objective, max_iterations=100000)
        else:
            raise UnknownMinimizerError(
                f"No {self.minimizer} minimizer for Theseus-ai "
            )

        self.th_optim = th.TheseusLayer(optimizer)

    def fit(self):
        """
        Run problem with Theseus
        """

        with torch.no_grad():
            _, self.th_info = self.th_optim.forward(
                self.th_inputs,
                optimizer_kwargs={
                    "track_best_solution": True,
                    "verbose": False,
                },
            )
        self._status = str(self.th_info.status[0])
        self.result = list(map(float, self.th_info.best_solution.values()))

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        if self._status == "NonlinearOptimizerStatus.CONVERGED":
            self.flag = 0
        elif self._status == "NonlinearOptimizerStatus.MAX_ITERATIONS":
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self.result
