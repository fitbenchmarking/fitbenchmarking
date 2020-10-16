"""
Implements the base class for the cost function class.
"""
from numpy import dot

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class NLLSCostFunc(CostFunc):
    """
    """

    def __init__(self, problem):
        """
        Initialise anything that is needed specifically for the new cost
        function.

        :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super(NLLSCostFunc, self).__init__(problem)
        #: *dict*
        #: Container cached residual evaluation
        self.cache_rx = {'params': None, 'value': None}

    def eval_r(self, params, x=None, y=None, e=None):
        """
        Calculate residuals and weight them if using errors

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: x data points, defaults to self.data_x
        :type x: numpy array, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array, optional

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """

        if x is None and y is None and e is None:
            x = self.problem.data_x
            y = self.problem.data_y
            e = self.problem.data_e
        elif x is None or y is None:
            raise CostFuncError('Residuals could not be computed with '
                                'only one of x and y.')

        result = y - self.problem.eval_model(params=params, x=x)
        if e is not None:
            result = result / e
        self.cache_rx['params'] = params
        self.cache_rx['value'] = result
        return result

    def eval_cost(self, params, x=None, y=None, e=None):
        """
        Evaluate the square of the L2 norm of the residuals

        :param params: The parameters to calculate residuals for
        :type params: list
        :param x: x data points, defaults to self.data_x
        :type x: numpy array, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array, optional

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        r = self.eval_r(params=params, x=x, y=y, e=e)

        self.cache_cost_x['params'] = params
        self.cache_cost_x['value'] = dot(r, r)
        return self.cache_cost_x['value']
