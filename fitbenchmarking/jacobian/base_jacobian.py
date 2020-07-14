"""
Implements the base class for the Jacobian.
"""
from abc import ABCMeta, abstractmethod
from numpy import array_equal, matmul


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

    def cached_func_values(self, cached_dict, eval_func, params, **kwargs):
        """
        Computes function values using cached or function evaluation

        :param cached_dict: Cached function values
        :type cached_dict: dict
        :param eval_func: Function to find the Jacobian for
        :type eval_func: Callable
        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Function evaluation
        :rtype: numpy array
        """
        if array_equal(params, cached_dict['params']):
            value = cached_dict['value']
        else:
            value = eval_func(params, **kwargs)
        return value

    def eval_r_norm(self, params, **kwargs):
        """
        Evaluates derivative of the cost function

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed derivative of the cost function
        :rtype: numpy array
        """
        fx = self.cached_func_values(self.problem.cache_fx,
                                     self.problem.eval_f,
                                     params,
                                     **kwargs)

        J = self.eval(params, **kwargs)
        out = matmul(J.T, fx)
        return out
