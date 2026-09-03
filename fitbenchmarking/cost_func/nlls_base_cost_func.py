"""
Implements the base non-linear least squares cost function
"""

from abc import abstractmethod

import numpy as np
from numpy import dot, matmul

from fitbenchmarking.cost_func.base_cost_func import CostFunc
from fitbenchmarking.utils.exceptions import CostFuncError


class BaseNLLSCostFunc(CostFunc):
    """
    This defines a base cost function for objectives of the type

    .. math:: \\min_p \\sum_{i=1}^n  r(y_i, x_i, p)^2

    where :math:`p` is a vector of length :math:`m`, and we start from a
    given initial guess for the optimal parameters.
    """

    def __init__(self, problem):
        r"""
        Initialise anything that is needed specifically for the new cost
        function.
        This defines a fitting problem where, given a set of :math:`n` data
        points :math:`(x_i,y_i)`, associated errors :math:`e_i`, and a model
        function :math:`f(x,p)`, we find the optimal parameters in the
        least-squares sense by solving:

        .. math:: \\min_p \\sum_{i=1}^n \\left( r(x) \\right)^2

        where :math:`p` is a vector of length :math:`m`, :math:`r(x)` is
        the calculated residual and we start from a
        given initial guess for the optimal parameters.
            :param problem: The parsed problem
        :type problem:
                :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

        """
        # Problem: The problem object from parsing
        super().__init__(problem)

        self.invalid_algorithm_types = ["MCMC"]

    @abstractmethod
    def eval_r_single_dataset(self, params, **kwargs):
        """
        Calculate residuals used in Least-Squares problems

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: The residuals for the datapoints at the given parameters
        :rtype: numpy array
        """
        raise NotImplementedError

    def _evaluating_combined_multifit(self, x) -> bool:
        """
        Check whether eval_r has been asked for the combined multifit
        problem rather than for a single dataset.

        The combined problem is being evaluated when the caller gives no
        x data (minimizers call eval_r with the parameters only) or gives
        the whole container of datasets. A single dataset's x values mean
        the params belong to that dataset alone, which is the case when
        eval_chisq scores each dataset in turn once the fit has finished.

        :param x: The x data eval_r was called with, if any
        :type x: numpy array, list of numpy arrays or None

        :return: True if the combined problem should be evaluated
        :rtype: bool
        """
        if not (self.problem.multifit and self.problem.multifit_param_names):
            return False
        return x is None or isinstance(x, (list, tuple)) or np.ndim(x) > 1

    def eval_r(self, params, **kwargs):
        """
        Calculates residuals used in Least-Squares problems.
        Handles both the multifit case (fitting multiple datasets)
        and other cases.

        :param params: The parameters to calculate residuals for
        :type params: list

        :return: The residuals for the datapoints at the given parameters
        :rtype: np.array
        """
        if not self._evaluating_combined_multifit(kwargs.get("x")):
            return self.eval_r_single_dataset(params, **kwargs)

        par_names = self.problem.multifit_param_names
        if len(params) != len(par_names):
            raise CostFuncError(
                "The number of parameters does not match the number of "
                f"MultiFit parameters, len(params)={len(params)} and "
                f"len(multifit_param_names)={len(par_names)}."
            )

        # Each dataset is evaluated with its own d<i>. params plus the
        # shared. params, and the residuals are joined into one vector.
        param_dict = dict(zip(par_names, params))
        r = [
            self.eval_r_single_dataset(
                params=[
                    v
                    for k, v in param_dict.items()
                    if k.startswith((f"d{d}.", "shared."))
                ],
                x=self.problem.data_x[d],
                y=self.problem.data_y[d],
                e=self.problem.data_e[d],
            )
            for d in range(len(self.problem.data_x))
        ]

        return np.concatenate(r)

    def eval_cost(self, params, **kwargs):
        """
        Evaluate the square of the L2 norm of the residuals,
        :math:`\\sum_i r(x_i,y_i,p)^2`
        at the given parameters

        :param params: The parameters, :math:`p`, to calculate residuals for
        :type params: list

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        r = self.eval_r(params=params, **kwargs)
        return dot(r, r)

    def jac_cost(self, params, **kwargs):
        """
        Uses the Jacobian of the model to evaluate the Jacobian of the
        cost function, :math:`\\nabla_p F(r(x,y,p))`, at the given
        parameters.

        :param params: The parameters at which to calculate Jacobians
        :type params: list

        :return: evaluated Jacobian of the cost function
        :rtype: 1D numpy array
        """
        r = self.eval_r(params, **kwargs)
        jacobian = self.jac_res(params, **kwargs)

        return 2.0 * jacobian.T.dot(r)

    def hes_cost(self, params, **kwargs):
        """
        Uses the Hessian of the model to evaluate the Hessian of the
        cost function, :math:`\\nabla_p^2 F(r(x,y,p))`, at the given
        parameters.

        :param params: The parameters at which to calculate Hessians
        :type params: list

        :return: evaluated Hessian of the cost function
        :rtype: 2D numpy array
        """
        r = self.eval_r(params, **kwargs)
        hessian, jacobian = self.hes_res(params, **kwargs)

        return 2.0 * (matmul(jacobian.T, jacobian) + matmul(hessian, r))
