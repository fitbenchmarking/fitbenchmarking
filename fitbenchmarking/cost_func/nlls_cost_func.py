"""
Implements the non-weighted non-linear least squares cost function
"""
from numpy import ravel

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class NLLSCostFunc(BaseNLLSCostFunc):
    """
    This defines the non-linear least squares cost function where, given a set
    of :math:`n` data points :math:`(x_i,y_i)`, associated errors :math:`e_i`,
    and a model function :math:`f(x,p)`, we find the optimal parameters in the
    root least-squares sense by solving:

    .. math:: \\min_p \\sum_{i=1}^n \\left(y_i - f(x_i, p)\\right)^2


    where :math:`p` is a vector of length :math:`m`, and we start from a
    given initial guess for the optimal parameters. More information on
    non-linear least squares cost functions can be found
    `here <https://en.wikipedia.org/wiki/Non-linear_least_squares>`__.
    """

    def eval_r(self, params, **kwargs):
        """
        Calculate the residuals, :math:`y_i - f(x_i, p)`

        :param params: The parameters, :math:`p`, to calculate residuals for
        :type params: list

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        if len(x) != len(y):
            raise CostFuncError('The length of the x and y are not the same, '
                                'len(x)={} and len(y)={}.'.format(len(x),
                                                                  len(y)))
        result = y - self.problem.eval_model(params=params, x=x)

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
        return - self.jacobian.eval(params, **kwargs)

    def hes_res(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function residual, :math:`\\nabla_p^2 r(x,y,p)`, at the
        given parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian and Jacobian of the residual at
        each x, y pair
        :rtype: tuple(list of 2D numpy arrays, list of 1D numpy arrays)
        """
        J = self.jac_res(params, **kwargs)
        return - self.hessian.eval(params, **kwargs), J
