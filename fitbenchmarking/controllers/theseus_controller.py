"""
Implements a controller for the Theseus fitting software.
"""

from typing import Iterable, List, Optional, Tuple ,Sequence
import theseus as th
import torch

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class TheseusCostFunction(th.CostFunction):
    def __init__(
        self,
        fb_cf,
        th_optim_vars, #: Iterable[th.Variable],
        # th_aux_vars,
        cost_weight: Optional[th.CostWeight] = None,
        name: Optional[str] = None,
        # aux_vars: Optional[Sequence[th.Variable]] = None,
    ):
        # if cost_weight is None:
        #     cost_weight = th.ScaleCostWeight(1.0)
        super().__init__(cost_weight, name=name)
        self.fb_cf = fb_cf
        self.th_optim_vars = th_optim_vars
        # self.th_aux_vars = aux_vars
        #print (" \n \n step 1 \n")
        if len(self.th_optim_vars) < 1:
            raise ValueError(
                "TheseusCostFunction must receive at least one optimization variable."
            )

        self.register_vars(self.th_optim_vars, is_optim_vars=True)
        #self.register_vars(self.th_aux_vars, is_optim_vars=False)
        #print (" \n step 2 \n")
        # self._tmp_optim_vars = tuple(v.copy() for v in self.th_optim_vars)
        # self._tmp_aux_vars = None
        # self._tmp_optim_vars_for_loop = None
        # self._tmp_aux_vars_for_loop = None

        self.x = [float(optim_vars1[0]) for optim_vars1 in self.th_optim_vars]
        # test = self.th_optim_vars.copy()
        # self._tmp_optim_vars = tuple(v.copy() for v in self.th_optim_vars)
        # print(test)
        # print(self._tmp_optim_vars)
        #print(self.x)
        #print (" \n step 3 \n")
        print(" \n \n values",self.x)
        print("out res",(th.Variable(self.fb_cf.eval_r(self.x), name="residuals")).tensor)
        print("out jac",(th.Variable(self.fb_cf.jac_res(self.x), name="jacobians")).tensor)
        print("fdsfs",self.fb_cf.jac_res(self.x))
        jacobian = self.fb_cf.jac_res(self.x)
        if jacobian is not None:
            jac = (th.Variable(jacobian, name="jacobians")).tensor
        print("check",jac)
    def error(self) -> torch.Tensor:
        print((th.Variable(self.fb_cf.eval_r(self.x), name="residuals")).tensor)
        #print("fsdfsdfds",(th.Variable(self.fb_cf.jac_res(self.x), name="jacobians")).tensor)
        print (" \n step error \n")
        return (th.Variable(self.fb_cf.eval_r(self.x), name="residuals")).tensor

    def jacobians(self) -> Tuple[List[torch.Tensor], torch.Tensor]:
        jacobian = self.fb_cf.jac_res(self.x)
        if jacobian is not None:
            jac = (th.Variable(jacobian, name="jacobians")).tensor
    
        return [jac], self.error()

    def dim(self) -> int:
        print("length",len(self.th_optim_vars))
        return len(self.th_optim_vars)

    def _copy_impl(self, new_name: Optional[str] = None) -> "TheseusCostFunction":
        return TheseusCostFunction(  # type: ignore
            self.th_optim_vars.copy(), self.weight.copy(), name=new_name
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
        self.result = None
        self._status = None
        self._popt = None
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
       
        x = th.Variable(self.data_x, name="x")
        y = th.Variable(self.data_y, name="y")
        th_aux_vars = x, y
        
        self.theseus_objective = th.Objective()
        
        th_optim_vars = [th.Vector(1,name=f"{name}") for name in self._param_names]

        self.theseus_cost_func = TheseusCostFunction(self.cost_func,th_optim_vars)

        self.theseus_objective.add(self.theseus_cost_func)

        if self.minimizer == 'Levenberg_Marquardt':
            optimizer = th.LevenbergMarquardt(self.theseus_objective,
                                              max_iterations=10000,
                                              step_size=0.5)
        if self.minimizer == 'Gauss-Newton':
            optimizer = th.GaussNewton(self.theseus_objective,
                                       max_iterations=10000, step_size=0.5)
        else:
            raise UnknownMinimizerError(
                "No {} minimizer for Ceres solver".format(self.minimizer))

        self.theseus_optim = th.TheseusLayer(optimizer)

    def fit(self):
        """
        Run problem with Theseus
        """

        params = [params*torch.ones((1, 1)) for params in self.initial_params]
        param_dict = dict(zip(self.problem.param_names, params))

        theseus_inputs = {
                            "x": self.data_x,
                            "y": self.data_y,
                            **param_dict}

        with torch.no_grad():
            _, self.theseus_info = self.theseus_optim.forward(
                theseus_inputs, optimizer_kwargs={"track_best_solution": True,
                                                  "verbose": True})

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        print(self.theseus_info.best_solution)
        self.final_params = self.theseus_info.best_solution
