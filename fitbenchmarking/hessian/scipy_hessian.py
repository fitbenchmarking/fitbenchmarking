"""
Module which calculates SciPy finite difference approximations
"""
from functools import lru_cache

import numpy as np
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.hessian.base_hessian import Hessian


class Scipy(Hessian):
    """
    Implements SciPy finite difference approximations to the derivative
    """

    # Problem formats that are incompatible with certain Scipy Hessians
    INCOMPATIBLE_PROBLEMS = {"cs": ["mantid"]}

    def eval(self, params, **kwargs):
        """
        Evaluates Hessian of problem.eval_model, returning the value
        \nabla^2_p f(x, p)

        :param params: The parameter values to find the Hessian at
        :type params: list

        :return: Approximation of the Hessian
        :rtype: 3D numpy array
        """
        x = kwargs.get("x", self.problem.data_x)
        hes = np.zeros((len(params), len(params), len(x)))

        @lru_cache
        def grad(params):
            return self.jacobian.eval(params)

        for i, _ in enumerate(x):
            # pylint: disable=cell-var-from-loop
            def grad_i(params):
                return grad(tuple(params))[i, :]
            hes[:, :, i] = approx_derivative(grad_i, params,
                                             method=self.method,
                                             rel_step=None,
                                             bounds=(-np.inf, np.inf),
                                             kwargs=kwargs)

        # ensure Hessian is symmetric
        return 0.5*(hes+hes.transpose(1, 0, 2))
