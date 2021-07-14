"""
Module which acts as an analytic Hessian calculator
"""
from numpy import matmul
import numpy as np

from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.utils.exceptions import NoHessianError


class Analytic(Hessian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, cost_func):
        super().__init__(cost_func)
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
        # e = kwargs.get("e", self.problem.data_e)
        rx = self.cached_func_values(self.cost_func.cache_rx,
                                     self.cost_func.eval_r,
                                     params,
                                     **kwargs)
        grad2_r = self.problem.hessian(x, params)
        # if self.problem.options.cost_func_type == "weighted_nlls":
        #     # scales each column of the Jacobian by the weights
        #     hes[:,:,0] = hes[:,:,0] / e[0]
        hes = matmul(grad2_r, rx)
        return hes

    def eval_cost(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        H = self.eval(params, **kwargs)
        J = self.jacobian.eval(params, **kwargs)
        out = H + matmul(np.transpose(J), J)
        return out
