"""
Module which calculates automatic differentiation derivatives using gvar
"""

import gvar as gv
import numpy as np

from fitbenchmarking.jacobian.base_jacobian import Jacobian
from fitbenchmarking.utils.exceptions import IncompatibleJacobianError


class Gvar(Jacobian):
    """
    Implements forward mode automatic differentiation using
    :code:`gvar` (https://gvar.readthedocs.io).

    This requires the model to be written entirely in operations that
    ``gvar.GVar`` overloads. Models which cast their parameters to float,
    or which call into compiled code, are not supported.
    """

    # gvar cannot differentiate through compiled or out of process models
    INCOMPATIBLE_PROBLEMS = {
        "forward_ad": ["cutest", "horace", "mantid", "mantiddev", "sasview"]
    }

    def __init__(self, problem):
        super().__init__(problem)
        self._seeds = None

    def eval(self, params, **kwargs):
        """
        Evaluates Jacobian of problem.eval_model

        :param params: The parameter values to find the Jacobian at
        :type params: list

        :return: Computed Jacobian
        :rtype: numpy array
        """
        num_params = len(params)
        # set up array of derivative seeds for gvar to use
        # in automatic differentiation
        if self._seeds is None or len(self._seeds) != num_params:
            self._seeds = gv.valder(num_params * [0.0])
        gvar_params = self._seeds + np.asarray(params, dtype=float)

        try:
            model = np.ravel(self.problem.eval_model(gvar_params, **kwargs))
            jac = np.array([model_i.der for model_i in model])
        except (TypeError, ValueError, AttributeError) as excp:
            raise IncompatibleJacobianError(
                "The gvar Jacobian could not differentiate the model for "
                f"problem format '{self.problem.format}'. The model must be "
                "written using operations that gvar.GVar supports, and must "
                "not cast its parameters to float or call compiled code. "
                f"The error was: {excp}"
            ) from excp

        return jac
