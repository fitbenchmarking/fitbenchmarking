"""
Module which acts as an analytic Hessian calculator
"""

from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.utils.exceptions import NoHessianError


class Analytic(Hessian):
    """
    Class to apply an analytic Hessian
    """

    def __init__(self, problem):
        super().__init__(problem)
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
        return self.problem.hessian(x, params)
