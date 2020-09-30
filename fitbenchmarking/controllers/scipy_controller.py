"""
Implements a controller for the scipy fitting software.
In particular, here for the scipy minimize solver for general minimization problems
"""

from scipy.optimize import minimize

from fitbenchmarking.controllers.base_controller import Controller


class ScipyController(Controller):
    """
    Controller for the Scipy fitting software.
    """

    def __init__(self, problem):
        """
        Initialises variable used for temporary storage.
        """
        super(ScipyController, self).__init__(problem)

        self._popt = None
        self.algorithm_check = {
            'all': ['Nelder-Mead', 'Powell', 'CG', 'BFGS', 'Newton-CG',
                    'L-BFGS-B', 'TNC', 'SLSQP'],
            'ls': [None],
            'deriv_free': ['Nelder-Mead', 'Powell'],
            'general': ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
                        'Newton-CG', 'L-BFGS-B', 'TNC', 'SLSQP']}

    def setup(self):
        """
        Setup problem ready to be run with SciPy
        """
        if self.minimizer == "lm-scipy":
            self.minimizer = "lm"

        self.options = {'maxiter': 500}

    def eval_jac(self, x, *args):
        """
        Wrapper for problem.eval_j to form the approximate Jacobian for
        problem.eval_r_norm

        :param x: The parameter values to find the Jacobian at
        :type x: list

        :return: Approximation of the Jacobian
        :rtype: numpy array
        """
        out = self.problem.jac.eval(params=x,
                                    func=self.problem.eval_r_norm,
                                    *args)
        return out

    def fit(self):
        """
        Run problem with Scipy.
        """
        # Neither the Nelder-Mead or Powell minimizers require a Jacobian
        # so are run without that argument.
        if self.minimizer == "Nelder-Mead" or self.minimizer == "Powell":
            self.result = minimize(fun=self.problem.eval_r_norm,
                                   x0=self.initial_params,
                                   method=self.minimizer,
                                   options=self.options)
        else:
            self.result = minimize(fun=self.problem.eval_r_norm,
                                   x0=self.initial_params,
                                   method=self.minimizer,
                                   jac=self.eval_jac,
                                   options=self.options)
        self._popt = self.result.x
        self._status = self.result.status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 0:
            self.flag = 0
        elif self._status == 2:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self._popt
