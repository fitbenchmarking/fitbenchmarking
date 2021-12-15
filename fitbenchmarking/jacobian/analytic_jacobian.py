"""
Module which acts as a analytic Jacobian calculator
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import NoJacobianError


class Analytic(Jacobian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, problem):
        super().__init__(problem)
        if not callable(self.problem.jacobian):
            raise NoJacobianError("Problem set selected does not currently "
                                  "support analytic Jacobians")

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        return self.problem.jacobian(x, params)

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return "analytic"
