"""
Module which acts as a analytic Jacobian calculator
"""
from typing import Any

from fitbenchmarking.jacobian.analytic_jacobian import Analytic
from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.jacobian.scipy_jacobian import Scipy


class BestAvailable(Jacobian):
    """
    Class to apply an analytical Jacobian if available -- otherwise choose a
    scipy one.
    """

    def __init__(self, problem):
        if callable(problem.jacobian):
            self.sub_jac = Analytic(problem)
        else:
            self.sub_jac = Scipy(problem)
            self.sub_jac.method = '2-point'

    def __getattribute__(self, __name: str) -> Any:
        if __name in ['sub_jac', 'name']:
            return super().__getattribute__(__name)
        return self.sub_jac.__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in ['sub_jac', 'name']:
            return super().__setattr__(__name, __value)
        if __name == 'method':
            return
        return setattr(self.sub_jac, __name, __value)

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return "best_available"
