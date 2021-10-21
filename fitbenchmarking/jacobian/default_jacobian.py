"""
Module which uses the minimizer's default jacobian
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian


# pylint: disable=useless-super-delegation
class Default(Jacobian):
    """
    Use the minimizer's jacobian/derivative approximation
    """

    def __init__(self, cost_func):
        super().__init__(cost_func)
        self.use_default_jac = True

    def eval(self, params, **kwargs):
        """
        This should not be called?
        """
        raise NotImplementedError
