"""
Implements the base class for the cost function class.
"""

from abc import ABCMeta, abstractmethod


class CostFunc:
    """
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
        #: Container cached function evaluation
        self.cache_fx = {'params': None, 'value': None}

        #: *dict*
        #: Container cached residual squared evaluation (cost function)
        self.cache_cost_x = {'params': None, 'value': None}

    @abstractmethod
    def eval_f(self, params, **kwargs):
        """
        Evaluates the model

        :param params: parameter value(s)
        :type params: list

        :return: data values evaluated from the model function of the problem
        :rtype: numpy array
        """
        raise NotImplementedError

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
