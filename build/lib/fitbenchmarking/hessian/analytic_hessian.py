"""
Module which acts as an analytic Hessian calculator
"""

from fitbenchmarking.hessian.base_hessian import Hessian
from fitbenchmarking.utils.exceptions import NoHessianError


class Analytic(Hessian):
    """
    Class to apply an analytic Hessian
    """

    def __init__(self, problem, jacobian):
        """
        Analytic hessian for problems.

        :param problem: The parsed problem.
        :type problem:
            :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
        :param jacobian: The jacobian for the problem
        :type jacobian: subclass of
            :class:`~fitbenchmarking.jacobian.base_jacobian`
        """
        super().__init__(problem, jacobian)
        if not callable(self.problem.hessian):
            raise NoHessianError("Problem set selected does not currently "
                                 "support analytic Hessians")

    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of problem.eval_model, returning the value
        \nabla^2_p f(x, p)

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Approximation of the Hessian
        :rtype: 3D numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        return self.problem.hessian(x, params)

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return "analytic"
