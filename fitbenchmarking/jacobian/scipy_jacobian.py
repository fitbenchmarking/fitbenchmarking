"""
Module which calculates SciPy finite difference approximations
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian


# pylint: disable=useless-super-delegation
class Scipy(Jacobian):
    """
    Implements SciPy finite difference approximations to the derivative
    """

    def __init__(self, problem):
        super(Scipy, self).__init__(problem)

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        func = self.problem.eval_r
        f0 = self.cached_func_values(self.problem.cache_rx,
                                     func,
                                     params,
                                     **kwargs)
        jac = approx_derivative(func, params, method=self.method,
                                rel_step=None, f0=f0,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
