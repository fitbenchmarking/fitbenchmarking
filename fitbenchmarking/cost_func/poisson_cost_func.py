"""
Implements a Poisson deviance cost function based on Mantid's:
https://docs.mantidproject.org/nightly/fitting/fitcostfunctions/Poisson.html
"""

import numpy as np

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.utils.exceptions import (
    CostFuncError,
    IncompatibleCostFunctionError,
)


class PoissonCostFunc(CostFunc):
    r"""
    This defines the Poisson deviance cost-function where,
    given the set of :math:`n` data points :math:`(x_i, y_i)`,
    and a model function :math:`f(x,p)`, we find the optimal parameters in the
    Poisson deviance sense by solving:

    .. math:: \min_p \sum_{i=1}^n
              \left( y_i \left(\log{y_i} - \log{f(x_i, p)} \right)
              - \left( y_i - f(x_i, p) \right) \right)

    where :math:`p` is a vector of length :math:`m`, and we start from a given
    initial guess for the optimal parameters.

    This cost function is intended for positive values.

    This cost function is not a least squares problem and as such will not work
    with least squares minimizers. Please use `algorithm_type` to select
    `general` solvers.
    See options docs (:ref:`fitting_option`) for information on how to do this.
    """

    def eval_cost(self, params, **kwargs):
        """
        Evaluate the Poisson deviance cost function

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: The x values to evaluate at. Default is self.problem.data_x
        :type x: np.array (optional)
        :param y: The y values to evaluate at. Default is self.problem.data_y
        :type y: np.array (optional)

        :return: evaluated cost function
        :rtype: float
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        if len(x) != len(y):
            raise CostFuncError(
                "The length of the x and y are not the same, "
                f"len(x)={len(x)} and len(y)= {len(y)}."
            )
        if (y < 0.0).any():
            raise CostFuncError(
                "This cost function is designed for use with "
                "positive experimental values, try again with "
                "a different cost function."
            )
        f_xp = self.problem.eval_model(x=x, params=params)

        # Penalise nagative f(x, p)
        f_xp[f_xp <= 0.0] = np.finfo(float).max

        residuals = _safe_a_log_b(y, y) - _safe_a_log_b(y, f_xp) - (y - f_xp)
        residuals = self.subtitute_nans(residuals)

        # Flatten in case of a vector function
        return sum(np.ravel(residuals))

    def jac_res(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        cost function residual, :math:`\\nabla_p r(x,y,p)`, at the
        given parameters.

        :param params: The parameters at which to calculate Jacobians
        :type params: list

        :return: evaluated Jacobian of the residual at each x, y pair
        :rtype: a list of 1D numpy arrays
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)

        jac = self.jacobian.eval(params, **kwargs)
        jac = self.subtitute_nans(jac)
        return jac * (1 - y / self.problem.eval_model(params, x=x))[:, None]

    def jac_cost(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        cost function, :math:`\\nabla_p F(r(x,y,p))`, at the given
        parameters.
        :param params: The parameters at which to calculate Jacobians
        :type params: list
        :return: evaluated Jacobian of the cost function
        :rtype: 1D numpy array
        """
        J = self.jac_res(params, **kwargs)
        J = self.subtitute_nans(J)
        return np.sum(J, 0)

    def hes_res(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function residual, :math:`\\nabla_p^2 r(x,y,p)`, at the
        given parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian and Jacobian of the residual at
                 each x, y pair
        :rtype: tuple (list of 2D numpy arrays, list of 1D numpy arrays)
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)

        f = self.problem.eval_model(params, x=x)
        jac = self.jacobian.eval(params, **kwargs)
        hes = self.hessian.eval(params, **kwargs)

        for i in range(len(x)):
            jac_i = np.array([jac[i]])
            hes[:, :, i] = hes[:, :, i] - y[i] / f[i] * (
                hes[:, :, i] - jac_i.T.dot(jac_i) / f[i]
            )
        hes = self.subtitute_nans(hes)
        return hes, self.jac_res(params, **kwargs)

    def hes_cost(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function, :math:`\\nabla_p^2 F(r(x,y,p))`, at the given
        parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian of the cost function
        :rtype: 2D numpy array
        """
        H, _ = self.hes_res(params, **kwargs)
        H = self.subtitute_nans(H)
        return np.sum(H, 2)

    def validate_problem(self):
        """
        Validate the problem for the Poisson Cost Function.
        Poisson involves a log so will fail on negative inputs.

        Raises:
            IncompatibleCostFunctionError: When the problem has negative
                                           values.
        """
        if (self.problem.data_y < 0).any():
            raise IncompatibleCostFunctionError(
                "Problem has a negative y value."
            )


def _safe_a_log_b(a, b):
    """
    Calculate y=a*log(b) such that if a==0 then y==0.
    """
    mask = a != 0

    result = a.copy().astype(np.float64)
    result[mask] *= np.log(b[mask])
    return result
