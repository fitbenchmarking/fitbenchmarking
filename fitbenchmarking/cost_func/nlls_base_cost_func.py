"""
Implements the base non-linear least squares cost function
"""
from numpy import dot

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.utils.exceptions import CostFuncError, IncompatibleMinimizerError
from abc import ABCMeta, abstractmethod


class BaseNLLSCostFunc(CostFunc):
    """
    """

    def __init__(self, problem):
        """
        Initialise anything that is needed specifically for the new cost
        function.
        This defines a fitting problem where, given a set of :math:`n` data
        points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
        function :math:`f(x,p)`, we find the optimal parameters in the
        least-squares sense by solving:

        .. math:: \min_p \sum_{i=1}^n \left( r(x) \right)^2

        where :math:`p` is a vector of length :math:`m`, :math:`r(x)` is
        the calculated residual and we start from a
        given initial guess for the optimal parameters.
            :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super(BaseNLLSCostFunc, self).__init__(problem)
        #: *dict*
        #: Container cached residual evaluation
        self.cache_rx = {'params': None, 'value': None}

        # Used to check whether the algorithm type of the 
        # selected minimizer is incompatible with the cost function
        self.invalid_algorithm_types = [None]

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
        Evaluate the square of the L2 norm of the residuals

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        r = self.eval_r(params=params, **kwargs)

        self.cache_cost_x['params'] = params
        self.cache_cost_x['value'] = dot(r, r)
        return self.cache_cost_x['value']

    def validate_algorithm_type(self,algorithm_check,minimizer):
        """
        Helper function which checks that the algorithm type of the
        selected minimizer from the options (options.minimizer)
        is incompatible with the selected cost function

        :param algorithm_check: dictionary object containing algorithm
        types and minimizers for selected software
        :type algorithm_check: dict
        :param minimizer: string of minimizers selected from the options
        :type minimizer: str
        """

        for alg_type in list(algorithm_check.keys()):
            if minimizer in algorithm_check[alg_type]:
                incompatible = alg_type in self.invalid_algorithm_types
                if incompatible:
                    message = 'The algorithm type of the selected ' \
                            'minimizer, {}, is not compatible with ' \
                            'the selected cost function'.format(minimizer)
                    raise IncompatibleMinimizerError(message)