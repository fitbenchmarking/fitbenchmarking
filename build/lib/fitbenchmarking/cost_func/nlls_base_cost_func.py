"""
Implements the base non-linear least squares cost function
"""
from abc import abstractmethod
from numpy import dot, matmul

from fitbenchmarking.cost_func.base_cost_func import CostFunc


class BaseNLLSCostFunc(CostFunc):
    """
    This defines a base cost function for objectives of the type

    .. math:: \\min_p \\sum_{i=1}^n  r(y_i, x_i, p)^2

    where :math:`p` is a vector of length :math:`m`, and we start from a
    given initial guess for the optimal parameters.
    """

    def __init__(self, problem):
        r"""
        Initialise anything that is needed specifically for the new cost
        function.
        This defines a fitting problem where, given a set of :math:`n` data
        points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
        function :math:`f(x,p)`, we find the optimal parameters in the
        least-squares sense by solving:

        .. math:: \\min_p \\sum_{i=1}^n \\left( r(x) \\right)^2

        where :math:`p` is a vector of length :math:`m`, :math:`r(x)` is
        the calculated residual and we start from a
        given initial guess for the optimal parameters.
            :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super().__init__(problem)

        self.invalid_algorithm_types = []

    @abstractmethod
    def eval_r(self, params, **kwargs):
        """
        Calculate residuals used in Least-Squares problems

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """
        raise NotImplementedError

    def eval_cost(self, params, **kwargs):
        """
        Evaluate the square of the L2 norm of the residuals,
        :math:`\\sum_i r(x_i,y_i,p)^2`
        at the given parameters

        :param params: The parameters, :math:`p`, to calculate residuals for
        :type params: list

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        r = self.eval_r(params=params, **kwargs)
        return dot(r, r)

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
        r = self.eval_r(params, **kwargs)
        J = self.jac_res(params, **kwargs)

        return 2.0 * matmul(J.T, r)

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
        r = self.eval_r(params, **kwargs)
        H, J = self.hes_res(params, **kwargs)

        return 2.0 * (matmul(J.T, J) + matmul(H, r))
