"""
Implements the whitened non-linear least squares cost function
"""

from functools import cached_property

from numpy import ravel
from scipy.linalg import cholesky, solve_triangular

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import (
    CostFuncError,
    IncompatibleCostFunctionError,
)


class WhitenedNLLSCostFunc(BaseNLLSCostFunc):
    """
    This defines the whitened non-linear least squares cost function where,
    given a set of :math:`n` data points :math:`(x_i,y_i)`, a full covariance
    matrix :math:`C` (stored in ``problem.additional_info['covariance']``), and
    a model function :math:`f(x,p)`, we find the optimal parameters by solving:

    .. math:: \\min_p (y - f(x, p))^T C^{-1} (y - f(x, p))

    which is equivalent to minimising the sum of squares of the whitened
    residuals :math:`L^{-1}(y - f(x,p))`, where :math:`L` is the lower
    Cholesky factor of :math:`C`.

    The covariance matrix must be positive-definite and stored in
    ``problem.additional_info['covariance']``.
    """

    def validate_problem(self):
        """
        Check that the problem provides a valid covariance matrix.

        :raises IncompatibleCostFunctionError: When the problem does not
            supply a covariance matrix.
        :raises CostFuncError: When the covariance matrix shape does not
            match the number of data points.
        """
        cov = self.problem.additional_info.get("covariance")
        if cov is None:
            raise IncompatibleCostFunctionError(
                "WhitenedNLLSCostFunc requires 'covariance' in "
                "problem.additional_info."
            )
        n = len(self.problem.data_y)
        if cov.shape != (n, n):
            raise CostFuncError(
                f"Covariance matrix shape {cov.shape} does not match "
                f"the number of data points ({n}). "
                "Check the covariance file for this problem."
            )

    @cached_property
    def _chol_L(self):  # noqa: N802
        """
        Compute and cache the lower Cholesky factor :math:`L` of the
        covariance matrix :math:`C`, such that :math:`C = L L^T`.

        :raises IncompatibleCostFunctionError: When the problem does not
            supply a covariance matrix.
        :rtype: 2D numpy array
        """
        cov = self.problem.additional_info.get("covariance")
        if cov is None:
            raise IncompatibleCostFunctionError(
                "WhitenedNLLSCostFunc requires 'covariance' in "
                "problem.additional_info."
            )
        return cholesky(cov, lower=True)

    def eval_r_single_dataset(self, params, **kwargs):
        """
        Calculate the whitened residuals, :math:`L^{-1}(y - f(x,p))`

        :param params: The parameters, :math:`p`, to calculate residuals for
        :type params: list

        :return: The whitened residuals for the data points at the given
                 parameters
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        if len(x) != len(y):
            raise CostFuncError(
                "The length of the x and y are not the same, "
                f"len(x)={len(x)} and len(y)={len(y)}."
            )
        r = ravel(y - self.problem.eval_model(params=params, x=x))
        return solve_triangular(self._chol_L, r, lower=True)

    def jac_res(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        whitened residuals, :math:`-L^{-1} J`, at the given parameters.

        :param params: The parameters at which to calculate Jacobians
        :type params: list

        :return: evaluated Jacobian of the whitened residuals, shape (n, m)
        :rtype: 2D numpy array
        """
        jac = self.jacobian.eval(params, **kwargs)
        return -solve_triangular(self._chol_L, jac, lower=True)

    def hes_res(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        whitened residuals at the given parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian and Jacobian of the whitened residuals
        :rtype: tuple (numpy array of shape (m, m, n), numpy array of
                shape (n, m))
        """
        hes = self.hessian.eval(params, **kwargs)
        # hes has shape (m, m, n); apply L^{-1} along the n axis:
        # for each (k1, k2), the vector hes[k1, k2, :] gets whitened.
        m, _, n = hes.shape
        hes_flat = hes.reshape(m * m, n)
        # solve_triangular applies L^{-1} to each column of the (n, m*m) matrix
        L_inv_flat = solve_triangular(  # noqa: N806
            self._chol_L, hes_flat.T, lower=True
        ).T
        return -L_inv_flat.reshape(m, m, n), self.jac_res(params, **kwargs)
