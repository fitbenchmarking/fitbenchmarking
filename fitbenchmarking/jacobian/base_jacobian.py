"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod

import numpy as np
from scipy.optimize._numdiff import approx_derivative


class Jacobian:
    """
    Base class for Jacobian.
    """
    __metaclass__ = ABCMeta

    def __init__(self, problem):
        self.problem = problem

    @abstractmethod
    def eval(self, params, func=None, **kwargs):
        """
        Evaluates Jacobian

        :param params: The parameter values to find the Jacobian at
        :type params: list
        :param func: Function to find the Jacobian for, defaults to
                     problem.eval_r
        :type func: Callable, optional

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        return NotImplementedError
