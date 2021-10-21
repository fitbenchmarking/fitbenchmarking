"""
Module which uses the minimizer's default jacobian
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian


# pylint: disable=useless-super-delegation
class Default(Jacobian):
    """
    Use the minimizer's jacobian/derivative approximation
    """

    def __init__(self, problem):
        super().__init__(problem)
        self.use_default_jac = True

    def eval(self, params, **kwargs):
        """
        This should not be called?
        """
        raise NotImplementedError
