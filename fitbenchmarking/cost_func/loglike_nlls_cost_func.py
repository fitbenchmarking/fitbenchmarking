"""
Implements the weighted non-linear least squares cost function,
to be used for Bayesian Fitting when evaluation of the
log-likelihood is required.
"""

from numpy import ravel

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class LoglikeNLLSCostFunc(BaseNLLSCostFunc):
    """
    This defines the weighted non-linear least squares cost function for
    Bayesian fitting where, given a set of :math:`n` data points
    :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
    function :math:`f(x,p)`, we find the optimal parameters in the root
    least-squares sense by solving:

    .. math:: \\min_p \\sum_{i=1}^n
              \\left(\\frac{y_i - f(x_i, p)}{e_i}\\right)^2

    where :math:`p` is a vector of length :math:`m`, and we start from a
    given initial guess for the optimal parameters. More information on
    non-linear least squares cost functions can be found
    `here <https://en.wikipedia.org/wiki/Non-linear_least_squares>`__.

    This cost function is intended for use with Bayesian fitting methods, where
    evaluation of the log-likelihood is required.
    """

    def __init__(self, problem):
        super().__init__(problem)
        self.invalid_algorithm_types = [
            "ls",
            "deriv_free",
            "general",
            "simplex",
            "trust_region",
            "levenberg-marquardt",
            "gauss_newton",
            "bfgs",
            "conjugate_gradient",
            "steepest_descent",
            "global_optimization",
        ]

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
        result = (y - self.problem.eval_model(params=params, x=x)) / e

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

    def eval_loglike(self, params):
        """
        Function to evaluate the log-likelihood of the cost function
        """
        return -1 / 2 * self.eval_cost(params)
