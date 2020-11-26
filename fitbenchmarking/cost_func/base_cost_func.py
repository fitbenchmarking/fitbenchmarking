"""
Implements the base class for the cost function class.
"""

from abc import ABCMeta, abstractmethod
from fitbenchmarking.utils.exceptions import CostFuncError


class CostFunc:
    """
    Base class for the cost functions.
    """

    __metaclass__ = ABCMeta

    def __init__(self, problem):
        """
        Initialise anything that is needed specifically for the new cost
        function.

        :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        self.problem = problem

        #: *dict*
        #: Container cached residual squared evaluation (cost function)
        self.cache_cost_x = {'params': None, 'value': None}

    @abstractmethod
    def eval_cost(self, params, **kwargs):
        """
        Evaluate the cost function

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: evaluated cost function
        :rtype: float
        """
        raise NotImplementedError
