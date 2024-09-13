"""
Module which calculates SciPy finite difference approximations
"""

import numpy as np
from scipy.optimize._numdiff import approx_derivative
from scipy.sparse import issparse

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import (
    NoSparseJacobianError,
    SparseJacobianIsDenseError,
)
from fitbenchmarking.utils.log import get_logger


class Scipy(Jacobian):
    """
    Implements SciPy finite difference approximations to the derivative
    """

    # Problem formats that are incompatible with certain Scipy Jacobians
    INCOMPATIBLE_PROBLEMS = {"cs": ["mantid"]}

    def __init__(self, problem):
        super().__init__(problem)
        self.jac_pattern = None
        self.equiv_np_method = None

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """

        self.equiv_np_method = self.method

        LOGGER = get_logger()

        if self.method.endswith("_sparse"):
            if self.problem.sparse_jacobian is None:
                raise NoSparseJacobianError(
                    f"The selected method is {self.method} but the "
                    "sparse_jacobian function is None. Please provide a "
                    "sparse jacobian function."
                )

            self.jac_pattern = self.problem.sparse_jacobian(self.problem.data_x, params)

            if not issparse(self.jac_pattern):
                raise SparseJacobianIsDenseError()

            # Remove the "_sparse" at the end
            self.equiv_np_method = self.method[:-7]

        else:
            if self.problem.sparse_jacobian is not None:
                LOGGER.info(
                    "Sparse_jacobian function found, but it "
                    "will not be used as the selected method is %s.",
                    self.method,
                )

        def func_wrapper(params, **kwargs):
            eval_model = self.problem.eval_model(params, **kwargs)
            return eval_model.ravel()

        jac = approx_derivative(
            func_wrapper,
            params,
            method=self.equiv_np_method,
            rel_step=None,
            bounds=(-np.inf, np.inf),
            kwargs=kwargs,
            sparsity=self.jac_pattern,
        )

        return jac
