"""
Implements the weighted non-linear least squares cost function
"""
from numpy import dot

from fitbenchmarking.cost_func.nlls_base_cost_func import BaseNLLSCostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class WeightedNLLSCostFunc(BaseNLLSCostFunc):
    """
    """

    def __init__(self, problem):
        """
        Initialise anything that is needed specifically for the new cost
        function.
        This defines a cost function where, given a set of :math:`n` data
        points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
        function :math:`f(x,p)`, we find the optimal parameters in the
        weighted least-squares sense by solving:

        .. math:: \min_p \sum_{i=1}^n \left(\frac{y_i - f(x_i, p)}{e}\right)^2

        where :math:`p` is a vector of length :math:`m`, and we start from a
        given initial guess for the optimal parameters.
            :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super(WeightedNLLSCostFunc, self).__init__(problem)
        #: *dict*
        #: Container cached residual evaluation
        self.cache_rx = {'params': None, 'value': None}

    def eval_r(self, params, **kwargs):
        """
        Calculate residuals

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        y = kwargs.get("y", self.problem.data_y)
        e = kwargs.get("e", self.problem.data_e)
        if len(x) != len(y) or len(x) != len(e):
            raise CostFuncError('The length of the x, y and e are not '
                                'the same, len(x)={}, len(y)={} and '
                                'len(e)={}'.format(len(x), len(y), len(e)))
        result = (y - self.problem.eval_model(params=params, x=x)) / e
        self.cache_rx['params'] = params
        self.cache_rx['value'] = result
        return result
