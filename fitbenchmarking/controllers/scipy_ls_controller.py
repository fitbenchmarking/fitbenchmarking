"""
Implements a controller for the scipy ls fitting software.
In particular, for the scipy least_squares solver.
"""

from scipy.optimize import least_squares

from fitbenchmarking.controllers.base_controller import Controller


class ScipyLSController(Controller):
    """
    Controller for the Scipy Least-Squares fitting software.
    """

    def __init__(self, problem):
        """
        Initialises variable used for temporary storage.
        """
        super(ScipyLSController, self).__init__(problem)

        self._popt = None
        self.algorithm_check = {
            'all': ['lm-scipy-no-jac', 'lm-scipy', 'trf', 'dogbox'],
            'ls': ['lm-scipy-no-jac', 'lm-scipy', 'trf', 'dogbox'],
            'deriv_free': [None],
            'general': [None]}

    def setup(self):
        """
        Setup problem ready to be run with SciPy LS
        """
        if self.minimizer == "lm-scipy":
            self.minimizer = "lm"

    def fit(self):
        """
        Run problem with Scipy LS.
        """
        # The minimizer "lm-scipy-no-jac" uses MINPACK's Jacobian evaluation
        # which are significantly faster and gives different results than
        # using the minimizer "lm-scipy" which uses problem.eval_j for the
        # Jacobian evaluation. We do not see significant speed changes or
        # difference in the accuracy results when running trf or dogbox with
        # or without problem.jac.eval for the Jacobian evaluation
        if self.minimizer == "lm-scipy-no-jac":
            self.result = least_squares(fun=self.problem.eval_r,
                                        x0=self.initial_params,
                                        method="lm",
                                        max_nfev=500)
        else:
            self.result = least_squares(fun=self.problem.eval_r,
                                        x0=self.initial_params,
                                        method=self.minimizer,
                                        jac=self.problem.jac.eval,
                                        max_nfev=500)

        self._popt = self.result.x
        self._status = self.result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status > 0:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._popt
