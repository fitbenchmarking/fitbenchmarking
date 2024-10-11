"""
Module which acts as a analytic Jacobian calculator
"""

from scipy.sparse import issparse

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import (
    NoJacobianError,
    NoSparseJacobianError,
    SparseJacobianIsDenseError,
)


class Analytic(Jacobian):
    """
    Class to apply an analytical Jacobian
    """

    def __init__(self, problem):
        super().__init__(problem)
        if not callable(self.problem.jacobian):
            raise NoJacobianError(
                """Problem set selected does not currently 
                support analytic Jacobians"""
            )

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)

        if self.method == "sparse":
            if self.problem.sparse_jacobian is None:
                raise NoSparseJacobianError(
                    f"The selected method is {self.method} but the "
                    "sparse_jacobian function is None. Please provide a "
                    "sparse jacobian function."
                )

            sparse_jac = self.problem.sparse_jacobian(x, params)

            if not issparse(sparse_jac):
                raise SparseJacobianIsDenseError()

            return sparse_jac

        return self.problem.jacobian(x, params)

    def name(self) -> str:
        """
        Get a name for the current status of the jacobian.

        :return: A unique name for this jacobian/method combination
        :rtype: str
        """
        return "analytic"
