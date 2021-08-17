"""
Module which acts as an analytic Hessian calculator
"""
from numpy import matmul
import numpy as np

from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.utils.exceptions import NoHessianError


class Analytic(Hessian):
    """
    Class to apply an analytic Hessian
    """

    def __init__(self, cost_func, jacobian):
        super().__init__(cost_func, jacobian)
        if not callable(self.problem.hessian):
            raise NoHessianError("Problem set selected does not currently "
                                 "support analytic Hessians")

    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of problem.eval_model, returning the value
        sum_{i=1}^m (r)_i \nabla^2r_i(x)

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Approximation of the Hessian
        :rtype: numpy array
        """

        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        e = kwargs.get("e", self.problem.data_e)
        grad2_r = self.problem.hessian(x, params)
        J = self.jacobian.eval(params, **kwargs)
        if self.problem.options.cost_func_type == "weighted_nlls":
            # scales the Hessian by the weights
            for i in range(len(e)):
                grad2_r[:, :, i] = grad2_r[:, :, i] / e[i]
        if self.problem.options.cost_func_type == "hellinger_nlls":
            model_eval = self.problem.eval_model(params, x=x)
            for i in range(len(x)):
                grad2_r[:, :, i] = 1/2*(
                    model_eval[i]**(-1/2))\
                    * grad2_r[:, :, i] + \
                    model_eval[i]**(-1/2)\
                    * np.matmul(J.T, J)
        if self.problem.options.cost_func_type == "poisson":
            model_eval = self.problem.eval_model(params, x=x)
            J = self.jacobian.eval_cost(params, **kwargs)
            for i in range(len(x)):
                grad2_r[:, :, i] = grad2_r[:, :, i]\
                    * (1-y[i]/model_eval[i])\
                    + (y[i]/model_eval[i]**2)\
                    * np.matmul(J.T, J)
            hes = np.sum(grad2_r, 2)

        if self.problem.options.cost_func_type != "poisson":
            rx = self.cached_func_values(self.cost_func.cache_rx,
                                         self.cost_func.eval_r,
                                         params,
                                         **kwargs)
            hes = matmul(grad2_r, rx)

        return hes, J

    def eval_cost(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        H, J = self.eval(params, **kwargs)
        if self.problem.options.cost_func_type != "poisson":
            out = H + matmul(np.transpose(J), J)
        else:
            out = H
        return out
