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
        # y = kwargs.get("y", self.problem.data_y)
        e = kwargs.get("e", self.problem.data_e)
        J = self.jacobian.eval(params, **kwargs)
        rx = self.cached_func_values(self.cost_func.cache_rx,
                                     self.cost_func.eval_r,
                                     params,
                                     **kwargs)
        grad2_r = self.problem.hessian(x, params)
        if self.problem.options.cost_func_type == "weighted_nlls":
            # scales the Hessian by the weights
            for i in range(len(e)):
                grad2_r[:, :, i] = grad2_r[:, :, i] / e[i]
        if self.problem.options.cost_func_type == "hellinger_nlls":
            for i in range(len(x)):
                grad2_r[:, :, i] = 1/2*(
                    self.problem.eval_model(params, x=x)**(-1/2))[i]\
                    * grad2_r[:, :, i] - \
                    1/2*(self.problem.eval_model(params, x=x)**(-3/2))[i]\
                    * np.matmul(J.T, J)

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
        out = H + matmul(np.transpose(J), J)
        return out
