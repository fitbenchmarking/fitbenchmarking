"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod


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
        Evaluate Jacobian
        """
        return NotImplementedError
