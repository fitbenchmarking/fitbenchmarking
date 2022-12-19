"""
Implements a controller for the Theseus fitting software.
"""

from typing import Iterable, List, Optional, Tuple ,Sequence
import theseus as th
import torch
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class TheseusCostFunction(th.CostFunction):
    def __init__(
        self,
        fb_cf,
        var,
        auxvar,
        cost_weight: Optional[th.CostWeight] = None,
        name: Optional[str] = None,
        # aux_vars: Optional[Sequence[th.Variable]] = None,
    ):
        if cost_weight is None:
            cost_weight = th.ScaleCostWeight(1.0)
        super().__init__(cost_weight, name=name)
        self.fb_cf = fb_cf
        self.var = var
        self.auxvar = auxvar or []

        if len(var) < 1:
            raise ValueError(
                "TheseusCostFunction must receive at least one optimization variable."
            )

        self.register_vars(var, is_optim_vars=True)
        self.register_vars(auxvar, is_optim_vars=False)

    def error(self) -> List[torch.Tensor]:

        optim_vars = tuple(v for v in self.optim_vars)
        optim_vars_list = [float(optim_vars1[0]) for optim_vars1 in optim_vars]
        res = self.fb_cf.eval_r(optim_vars_list) 
        th_res = torch.Tensor(np.array([res]))
        return th_res, optim_vars_list

    def jacobians(self) -> Tuple[List[torch.Tensor], torch.Tensor]:
        err, optim_vars_list = self.error()
        jacs = self.fb_cf.jac_res(optim_vars_list)
        #print(f"{jacs=}") 
        th_jac = [torch.Tensor([[[item] for item in jacs[:,index]]]) for index in range(len(optim_vars_list))]
        return th_jac, err

    def dim(self) -> int:
        x_data = self.auxvar[0].tensor.numpy()
        return len(x_data[0])

    def _copy_impl(self, new_name: Optional[str] = None) -> "TheseusCostFunction":
        return TheseusCostFunction(  # type: ignore
            var=[v.copy() for v in self.var],
            auxvar=[v.copy() for v in self.auxvar],
            cost_weight=self.weight.copy(),
            name=new_name,
            fb_cf=self.fb_cf
        )


class TheseusController(Controller):
    """
    Controller for Theseus
    """

    algorithm_check = {
        'all': ['Levenberg_Marquardt', 'Gauss-Newton'],
        'ls': ['Levenberg_Marquardt', 'Gauss-Newton'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': ['Levenberg_Marquardt'],
        'gauss_newton': ['Gauss-Newton'],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': []
    }

    jacobian_enabled_solvers = ['Levenberg_Marquardt', 'Gauss-Newton']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self._status = None
        self.theseus_objective = None
        self.theseus_optim = None
        self.data_x = self.problem.data_x
        self.data_y = self.problem.data_y
        self.theseus_info = None
        self.theseus_cost_func = None
        self._param_names = self.problem.param_names


    def setup(self):
        """
        Setup problem ready to be run with Theseus
        """
       
        x = th.Variable(torch.from_numpy(np.array([self.data_x])).float(), name="x_data")
        y = th.Variable(torch.from_numpy(np.array([self.data_y])).float(), name="y_data")

        th_aux_vars = x, y
        
        self.theseus_objective = th.Objective()
        
        th_optim_vars = [th.Vector(1,name=f"{name}") for name in self._param_names]

        self.theseus_cost_func =  TheseusCostFunction(self.cost_func, th_optim_vars, th_aux_vars, name="theseus")

        self.theseus_objective.add(self.theseus_cost_func)
        if self.minimizer == 'Levenberg_Marquardt':
            optimizer = th.LevenbergMarquardt(self.theseus_objective,
                                              max_iterations=100000,
                                              step_size=0.5)
        elif self.minimizer == 'Gauss-Newton':
            optimizer = th.GaussNewton(self.theseus_objective,
                                       max_iterations=100000, step_size=0.5)
        else:
            raise UnknownMinimizerError(
                "No {} minimizer for Theseus-ai ".format(self.minimizer))

        self.theseus_optim = th.TheseusLayer(optimizer)

    def fit(self):
        """
        Run problem with Theseus
        """

        params = [params*torch.ones((1, 1)) for params in self.initial_params]
        param_dict = dict(zip(self.problem.param_names, params))

        theseus_inputs = {
                            "x_data": torch.from_numpy(np.array([self.data_x])).float(),
                            "y_data": torch.from_numpy(np.array([self.data_y])).float(),
                            **param_dict}

        with torch.no_grad():
            _, self.theseus_info = self.theseus_optim.forward(
                theseus_inputs, optimizer_kwargs={"track_best_solution": True,
                                                  "verbose": False})

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        self._status = str(self.theseus_info.status[0])
        if self._status == "NonlinearOptimizerStatus.CONVERGED":
            self.flag = 0
        elif self._status == "NonlinearOptimizerStatus.MAX_ITERATIONS":
            self.flag = 1
        else:
            self.flag = 2


        self.final_params = list(map(float,self.theseus_info.best_solution.values()))
