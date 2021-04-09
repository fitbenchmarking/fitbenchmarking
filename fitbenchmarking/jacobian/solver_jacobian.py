"""
Module which uses the solver's default jacobian
"""
from fitbenchmarking.jacobian.base_jacobian import Jacobian

# pylint: disable=useless-super-delegation
class solver(Jacobian):
    """
    Use the solver jacobian/derivative approximation
    """

    def __init__(self, cost_func):
        super(solver, self).__init__(cost_func)
        self.use_solver_jac = True

