"""
Module which calculates SciPy complex steps numerical method
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian


# pylint: disable=useless-super-delegation
class ScipyCS(Jacobian):
    """
    Implements SciPy complex steps numerical method for calculating the
    derivative
    """

    def __init__(self, problem):
        super(ScipyCS, self).__init__(problem)

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
        if func is None:
            func = self.problem.eval_r

        jac = approx_derivative(func, params, method="cs",
                                rel_step=None, f0=func(params, **kwargs),
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
