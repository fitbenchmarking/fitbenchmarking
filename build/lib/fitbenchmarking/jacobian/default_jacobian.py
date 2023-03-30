"""
Module which uses the minimizer's default jacobian
"""
from fitbenchmarking.jacobian.scipy_jacobian import Scipy


class Default(Scipy):
    """
    Use the minimizer's jacobian/derivative approximation
    """

    def __init__(self, problem):
        super().__init__(problem)
        self.use_default_jac = True

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        self.method = "2-point"
        return super().eval(params, **kwargs)

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return ""
