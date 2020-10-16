"""
Module which acts as a analytic Jacobian calculator
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError

from numpy import matmul


# pylint: disable=useless-super-delegation
class Analytic(Jacobian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, cost_func):
        super(Analytic, self).__init__(cost_func)
        if not callable(self.problem.jacobian):
            raise NoJacobianError("Problem set selected does not currently "
                                  "support analytic Jacobians")

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of cost_func.eval_f or a weighted cost_func.eval_f

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        e = kwargs.get("e", self.problem.data_e)
        jac = self.problem.jacobian(x, params)

        if self.problem.options.use_errors:
            # scales each column of the Jacobian by the weights
            jac = jac / e[:, None]

        return jac

    def eval_cost(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        rx = self.cached_func_values(self.cost_func.cache_rx,
                                     self.cost_func.eval_r,
                                     params,
                                     **kwargs)
        J = self.eval(params, **kwargs)
        out = 2.0 * matmul(J.T, rx)
        return out
