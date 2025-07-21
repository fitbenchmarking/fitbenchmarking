"""
Implements the weighted non-linear least squares cost function
"""

import numpy as np
from numpy import ravel
from scipy.sparse import issparse

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class WeightedNLLSCostFunc(BaseNLLSCostFunc):
    """
    This defines the weighted non-linear least squares cost function where,
    given a set of :math:`n` data points :math:`(x_i,y_i)`, associated errors
    :math:`e_i`, and a model function :math:`f(x,p)`, we find the optimal
    parameters in the root least-squares sense by solving:

    .. math:: \\min_p \\sum_{i=1}^n
              \\left(\\frac{y_i - f(x_i, p)}{e_i}\\right)^2

    where :math:`p` is a vector of length :math:`m`, and we start from a
    given initial guess for the optimal parameters. More information on
    non-linear least squares cost functions can be found
    `here <https://en.wikipedia.org/wiki/Non-linear_least_squares>`__.
    """

    def eval_r(self, params, **kwargs):
        """
        Calculate the residuals, :math:`\\frac{y_i - f(x_i, p)}{e_i}`

        :param params: The parameters, :math:`p`, to calculate residuals for
        :type params: list

        :return: The residuals for the data points at the given parameters
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        e = kwargs.get("e", self.problem.data_e)
        if len(x) != len(y) or len(x) != len(e):
            raise CostFuncError(
                "The length of the x, y and e are not "
                f"the same, len(x)={len(x)}, len(y)={len(y)}"
                f" and len(e)={len(e)}"
            )

        mask = ravel(self.problem.mask)
        # recon_y = np.full(np.shape(mask), np.nan)
        # recon_y[~mask] = y
        # recon_x = np.full(np.shape(mask), np.nan)
        # recon_x[~mask] = x
        # recon_e = np.full(np.shape(mask), np.nan)
        # recon_e[~mask] = e
        # result = (
        # ravel(recon_y) - self.problem.eval_model(params=params,
        # x=ravel(recon_x))) / ravel(recon_e)

        # y = np.ma.MaskedArray(y, mask=mask).compressed()
        # eval_y = self.problem.eval_model(params=params, x=x)
        # eval_y = np.ma.MaskedArray(eval_y, mask=mask).compressed()
        # e = np.ma.MaskedArray(e, mask=mask).compressed()
        # print(np.shape(y))
        # print(np.shape(eval_y))
        # print(np.shape(e))
        # result = (y - eval_y) / e

        ####################
        y[mask] = 0
        eval_y = self.problem.eval_model(params=params, x=x)
        eval_y[mask] = 0
        # e[mask] = 1
        result = (y - eval_y) / e

        result = np.nan_to_num(result, nan=0)

        # Flatten in case of a vector function
        return ravel(result)

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
        e = kwargs.get("e", self.problem.data_e)

        jac = self.jacobian.eval(params, **kwargs)

        if issparse(jac):
            return -jac.transpose().multiply(1 / e).transpose()

        return -jac / e[:, None]

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
        e = kwargs.get("e", self.problem.data_e)

        hes = self.hessian.eval(params, **kwargs)
        for i, e_i in enumerate(e):
            hes[:, :, i] = -hes[:, :, i] / e_i

        return hes, self.jac_res(params, **kwargs)
