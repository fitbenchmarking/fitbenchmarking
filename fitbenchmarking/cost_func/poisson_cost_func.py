"""
Implements a Poisson deviance cost function based on Mantid's:
https://docs.mantidproject.org/nightly/fitting/fitcostfunctions/Poisson.html
"""
from numpy import log, finfo, float64

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


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
    See options docs (:ref:`fitting-option`) for information on how to do this.
    """

    def __init__(self, problem):
        """
        Initialise the poisson cost function class

        :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super().__init__(problem)

    def eval_cost(self, params, **kwargs):
        """
        Evaluate the cost function

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
            raise CostFuncError('The length of the x and y are not the same, '
                                'len(x)={} and len(y)= {}.'.format(len(x),
                                                                   len(y)))
        if (y < 0.0).any():
            raise CostFuncError('This cost function is designed for use with '
                                'positive experimental values, try again with '
                                'a different cost function.')
        f_xp = self.problem.eval_model(x=x, params=params)

        # Penalise nagative f(x, p)
        f_xp[f_xp <= 0.0] = finfo(float).max

        result = sum(_safe_a_log_b(y, y) - _safe_a_log_b(y, f_xp) - (y - f_xp))
        self.cache_cost_x['params'] = params
        self.cache_cost_x['value'] = result
        return result


def _safe_a_log_b(a, b):
    """
    Calculate y=a*log(b) such that if a==0 then y==0.
    """
    mask = a != 0

    result = a.copy().astype(float64)
    result[mask] *= log(b[mask])
    return result
