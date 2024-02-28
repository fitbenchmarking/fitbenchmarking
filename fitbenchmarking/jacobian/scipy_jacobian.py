"""
Module which calculates SciPy finite difference approximations
"""
import numpy as np
from scipy.optimize._numdiff import approx_derivative
from scipy.sparse import issparse

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import (NoSparseJacobianError,
                                              SparseJacobianIsDenseError)
from fitbenchmarking.utils.log import get_logger


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

        LOGGER = get_logger()
        self.jac_pattern = None
        self.method_new = self.method

        if self.method.endswith("_sparse"):

            if self.problem.sparse_jacobian is None:

                # shall we use NoAnalyticJacobian here?
                raise NoSparseJacobianError(
                    f'The selected method is {self.method} but the '
                    'sparse_jacobian function is None. Please provide a '
                    'sparse jacobian function.')

            self.jac_pattern = self.problem.\
                sparse_jacobian(self.problem.data_x, params)

            if not issparse(self.jac_pattern):
                raise SparseJacobianIsDenseError()

            # Remove the "_sparse" at the end
            self.method_new = self.method[:-7]

        else:
            if self.problem.sparse_jacobian is not None:
                LOGGER.info('Sparse_jacobian function found, but it '
                            'will not be used as the selected method is '
                            f'{self.method}.')

        func = self.problem.eval_model
        jac = approx_derivative(func, params, method=self.method_new,
                                rel_step=None,
                                bounds=(-np.inf, np.inf),
                                kwargs=kwargs,
                                sparsity=self.jac_pattern)

        return jac
