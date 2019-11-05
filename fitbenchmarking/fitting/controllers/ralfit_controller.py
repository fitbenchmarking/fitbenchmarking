"""
Implements a controller for RALFit
https://github.com/ralna/RALFit
"""

import ral_nlls
from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.fitting.controllers.base_controller import Controller


class RALFitController(Controller):
    """
    Controller for the RALFit fitting software.
    """

    def __init__(self, problem, use_errors):
        """
        Initialises variable used for temporary storage.
        """
        super(RALFitController, self).__init__(problem, use_errors)

        self._x = None
        self._inform = None

    def setup(self):
        """
        Setup for RALFit
        """
        pass

    def _eval_f_arg_swap(self, params, x):
        return self.problem.eval_f(x=x,
                                   params=params,
                                   function_id=self.function_id)

    def _prediction_error(self, params, x, y):
        return self._eval_f_arg_swap(params, x) - y

    def _jac(self, params, x, y):
        return approx_derivative(self._eval_f_arg_swap,
                                 params,
                                 args=tuple([x]))

    def fit(self):
        """
        Run problem with RALFit.
        """
        self.success = False
        try:
            (self._x, self._inform) = ral_nlls.solve(self.initial_params,
                                                     self._prediction_error,
                                                     self._jac,
                                                     params=(self.data_x,
                                                             self.data_y))
            self.success = True
        except:
            self.success = False

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self.success:
            self.results = self.problem.eval_f(x=self.data_x,
                                               params=self._x,
                                               function_id=self.function_id)
            self.final_params = self._x
