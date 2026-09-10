"""
Implements the base non-linear least squares cost function
"""

from abc import abstractmethod

from numpy import concatenate, dot, matmul, ndim

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

        This is only consulted when the caller has not named a dataset
        with the 'dataset' keyword argument. The combined problem is being
        evaluated when the caller gives no x data (minimizers call eval_r
        with the parameters only) or gives the whole container of
        datasets. A single dataset's x values mean the params belong to
        that dataset alone, which is the case when eval_chisq scores each
        dataset in turn once the fit has finished.

        :param x: The x data eval_r was called with, if any
        :type x: numpy array, list of numpy arrays or None

        :return: True if the combined problem should be evaluated
        :rtype: bool
        """
        if not (self.problem.multifit and self.problem.multifit_param_names):
            return False
        return x is None or isinstance(x, (list, tuple)) or ndim(x) > 1

    def eval_r(self, params, **kwargs):
        """
        Calculates residuals used in Least-Squares problems.
        Handles both the multifit case (fitting multiple datasets)
        and other cases.

        In the multifit case the parameters of every dataset are given as
        one combined vector, and the residuals of all of the datasets are
        returned one after the other. A single dataset of a multifit
        problem can be evaluated by naming it with the 'dataset' keyword
        argument, in which case 'params' holds the parameters of that
        dataset only.

        :param params: The parameters to calculate residuals for
        :type params: list
        :param dataset: The index of the single dataset to evaluate,
                        defaults to None (all of them)
        :type dataset: int, optional

        :raises CostFuncError: If the combined problem is evaluated with a
                               parameter vector of the wrong length.

        :return: The residuals for the datapoints at the given parameters
        :rtype: np.array
        """
        # A named dataset always means a single dataset of a multifit
        # problem, whose parameters have already been split out of the
        # combined vector by the caller. Where the caller has not named
        # one, fall back to working it out from the shape of the x data.
        named_dataset = kwargs.get("dataset") is not None
        if named_dataset or not self._evaluating_combined_multifit(
            kwargs.get("x")
        ):
            return self.eval_r_single_dataset(params, **kwargs)

        par_names = self.problem.multifit_param_names
        if len(params) != len(par_names):
            raise CostFuncError(
                "The number of parameters does not match the number of "
                f"MultiFit parameters, len(params)={len(params)} and "
                f"len(multifit_param_names)={len(par_names)}."
            )

        r = []
        param_dict = dict(zip(par_names, params))
        for d in range(len(self.problem.data_x)):
            single_dataset_params = [
                v
                for k, v in param_dict.items()
                if k.startswith((f"d{d}.", "shared."))
            ]

            kwargs["x"] = self.problem.data_x[d]
            kwargs["y"] = self.problem.data_y[d]
            kwargs["e"] = self.problem.data_e[d]
            kwargs["dataset"] = d

            r.append(
                self.eval_r_single_dataset(
                    params=single_dataset_params, **kwargs
                )
            )

        # the residuals of the datasets are returned as one flat array, as
        # some of the fitting softwares require an array rather than a list
        return concatenate(r)

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
        J = self.jac_res(params, **kwargs)

        return 2.0 * J.T.dot(r)

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
        H, J = self.hes_res(params, **kwargs)

        return 2.0 * (matmul(J.T, J) + matmul(H, r))
