"""
Implements the base class for the cost function class.
"""

from abc import ABCMeta, abstractmethod
from fitbenchmarking.utils.exceptions import CostFuncError, IncompatibleMinimizerError


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

        # Used to check whether the algorithm type of the 
        # selected minimizer is incompatible with the cost function
        self.invalid_algorithm_types = [None]

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

    def validate_algorithm_type(self, algorithm_check, minimizer):
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
