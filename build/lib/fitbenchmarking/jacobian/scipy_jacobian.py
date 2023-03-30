"""
Module which calculates SciPy finite difference approximations
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.jacobian.base_jacobian import Jacobian


class Scipy(Jacobian):
    """
    Implements SciPy finite difference approximations to the derivative
    """

    # Problem formats that are incompatible with certain Scipy Jacobians
    INCOMPATIBLE_PROBLEMS = {"cs": ["mantid"]}

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        func = self.problem.eval_model
        jac = approx_derivative(func, params, method=self.method,
                                rel_step=None,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs)
        return jac
