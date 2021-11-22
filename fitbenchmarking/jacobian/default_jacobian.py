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
        self.method = "2-point"
