"""
Implements a controller for GSL
https://www.gnu.org/software/gsl/
using the pyGSL python interface
https://sourceforge.net/projects/pygsl/
"""
import numpy as np

from pygsl import multifit_nlin, multiminimize, errno
from pygsl import _numobj as numx

from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


class GSLController(Controller):
    """
    Controller for the GSL fitting software
    """

    def __init__(self, problem):
        """
        Initializes variable used for temporary storage

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(GSLController, self).__init__(problem)

        self._solver = None
        self._residual_methods = None
        self._function_methods_no_jac = None
        self._function_methods_with_jac = None
        self._gradient_tol = None
        self._abserror = None
        self._relerror = None
        self._maxits = None
        self.algorithm_check = {
            'all': ['lmsder', 'lmder', 'nmsimplex', 'nmsimplex2',
                    'conjugate_pr', 'conjugate_fr', 'vector_bfgs',
                    'vector_bfgs2', 'steepest_descent'],
            'ls': ['lmsder', 'lmder'],
            'deriv_free': ['nmsimplex', 'nmsimplex2'],
            'general': ['nmsimplex', 'nmsimplex2', 'conjugate_pr',
                        'conjugate_fr', 'vector_bfgs', 'vector_bfgs2',
                        'steepest_descent']}

    def _prediction_error(self, p, data=None):
        """
        Utility function to call problem.eval_r with correct args

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from problem.eval_r
        :rtype: numpy array
        """
        return self.problem.eval_r(p)

    def _jac(self, p, data=None):
        """
        Utility function to call jac.eval with correct args

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from jac.eval
        :rtype: numpy array
        """
        return self.problem.jac.eval(p)

    def _fdf(self, p, data=None):
        """
        Utility function to return results from eval_r and eval_j as a tuple.

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from problem.eval_r and eval_j
        :rtype: (numpy array, numpy array)
        """
        f = self.problem.eval_r(p)
        df = self.problem.jac.eval(p)
        return f, df

    def _chi_squared(self, p, data=None):
        """
        Utility function to call problem.eval_r_norm with correct args

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from problem.eval_r_norm
        :rtype: numpy array
        """
        return self.problem.eval_r_norm(p)

    def _jac_chi_squared(self, p, data=None):
        """
        Utility function to get jacobian for problem.eval_r_norm

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: jacobian approximation for problem.eval_r_norm
        :rtype: numpy array
        """
        j = approx_derivative(self.problem.eval_r_norm, p)
        return j

    def _chi_squared_fdf(self, p, data=None):
        """
        Utility function to return results from eval_r_norm and
        _jac_chi_squared as a tuple.

        :param p: parameters
        :type p: list
        :param data: x data, this is discarded as the defaults can be used.
        :type data: N/A
        :return: result from problem.eval_r_norm and _jac_chi_squared
        :rtype: (numpy array, numpy array)
        """
        f = self.problem.eval_r_norm(p)
        df = self._jac_chi_squared(p)
        return f, df

    def setup(self):
        """
        Setup for GSL
        """
        data = numx.array([self.data_x,
                           self.data_y,
                           self.data_e])
        n = len(self.data_x)
        p = len(self.initial_params)
        pinit = numx.array(self.initial_params)

        self._residual_methods = ['lmsder',
                                  'lmder']
        self._function_methods_no_jac = ['nmsimplex',
                                         'nmsimplex2']
        self._function_methods_with_jac = ['conjugate_pr',
                                           'conjugate_fr',
                                           'vector_bfgs',
                                           'vector_bfgs2',
                                           'steepest_descent']

        # set up the system
        if self.minimizer in self._residual_methods:
            mysys = multifit_nlin.gsl_multifit_function_fdf(
                self._prediction_error,
                self._jac,
                self._fdf,
                data,
                n,
                p)
            self._solver = getattr(multifit_nlin, self.minimizer)(mysys, n, p)
        elif self.minimizer in self._function_methods_no_jac:
            mysys = multiminimize.gsl_multimin_function(self._chi_squared,
                                                        data,
                                                        p)
            self._solver = getattr(multiminimize, self.minimizer)(mysys, p)
        elif self.minimizer in self._function_methods_with_jac:
            mysys = multiminimize.gsl_multimin_function_fdf(
                self._chi_squared,
                self._jac_chi_squared,
                self._chi_squared_fdf,
                data,
                p)
            self._solver = getattr(multiminimize, self.minimizer)(mysys, p)
        else:
            raise UnknownMinimizerError(
                "No {} minimizer for GSL".format(self.minimizer))

        # Set up initialization parameters
        #
        # These have been chosen to be consistent with the parameters
        # used in Mantid.
        initial_steps = 1.0 * numx.array(np.ones(p))
        step_size = 0.1
        tol = 1e-4
        self._gradient_tol = 1e-3
        self._abserror = 1e-4
        self._relerror = 1e-4
        self._maxits = 500

        if self.minimizer in self._residual_methods:
            self._solver.set(pinit)
        elif self.minimizer in self._function_methods_no_jac:
            self._solver.set(pinit, initial_steps)
        else:
            self._solver.set(pinit, step_size, tol)

    def fit(self):
        """
        Run problem with GSL
        """
        for _ in range(self._maxits):
            status = self._solver.iterate()
            # check if the method has converged
            if self.minimizer in self._residual_methods:
                x = self._solver.getx()
                dx = self._solver.getdx()
                status = multifit_nlin.test_delta(dx, x,
                                                  self._abserror,
                                                  self._relerror)
            elif self.minimizer in self._function_methods_no_jac:
                simplex_size = self._solver.size()
                status = multiminimize.test_size(simplex_size,
                                                 self._abserror)
            else:  # must be in function_methods_with_jac
                gradient = self._solver.gradient()
                status = multiminimize.test_gradient(gradient,
                                                     self._gradient_tol)
            if status == errno.GSL_SUCCESS:
                self.flag = 0
                break
            elif status != errno.GSL_CONTINUE:
                self.flag = 2
        else:
            self.flag = 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        self.final_params = self._solver.getx()
