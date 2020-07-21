"""
Module which calculates SciPy 3 point finite difference approximation
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian

# pylint: disable=useless-super-delegation


class ScipyThreePoint(Jacobian):
    """
    Implements SciPy 3 point finite difference approximation to the derivative
    """

    def __init__(self, problem):
        super(ScipyThreePoint, self).__init__(problem)

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
        jac = approx_derivative(func, params, method="3-point",
                                rel_step=None, f0=f0,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
