"""
Implements a controller for GSL
https://www.gnu.org/software/gsl/
using the pyGSL python interface
https://sourceforge.net/projects/pygsl/
"""

import pygsl
from pygsl import multifit_nlin, multiminimize, errno
from pygsl import _numobj as numx
import numpy as np

from scipy.optimize._numdiff import approx_derivative

from fitbenchmarking.fitting.controllers.base_controller import Controller

class GSLController(Controller):
    """
    Controller for the GSL fitting software
    """

    def __init__(self, problem, use_errors):
        """
        Initializes variable used for temporary storage
        """
        super(GSLController, self).__init__(problem, use_errors)
        self._pinit = None
        self._solver = None

    def _prediction_error(self, p, data=None):
        f = self.problem.eval_f(x=self.data_x,
                                params=p,
                                function_id=self.function_id)
        f = f - self.data_y
        if self.use_errors:
            f = f / self.data_e
            
        return f

    def _jac(self, p, data=None):
        j = approx_derivative(self._prediction_error,
                              p)
        return j

    def _fdf(self, p, data=None):
        f  = self._prediction_error(p)
        df = self._jac(p)
        return f, df

    def _chi_squared(self, p, data=None):
        f = self._prediction_error(p)
        return np.dot(f,f)

    def _jac_chi_squared(self, p, data=None):
        j = approx_derivative(self._chi_squared,
                              p)
        return j

    def _chi_squared_fdf(self, p, data=None):
        f  = self._chi_squared(p)
        df = self._jac_chi_squared(p)
        return f, df
        
    def setup(self):
        """
        Setup for GSL
        """
        self._data = numx.array([self.data_x,
                                 self.data_y,
                                 self.data_e])
        self._n = len(self.data_x)
        self._p = len(self.initial_params)
        self._pinit = numx.array(self.initial_params)

        self._residual_methods = ['lmsder',
                                  'lmder']
        self._function_methods_no_jac = ['simplex',
                                         'simplex2']
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
                self._data,
                self._n,
                self._p)
        elif self.minimizer in self._function_methods_no_jac:
            mysys = multiminimize.gsl_multimin_function(self._chi_squared,
                                                        self._pinit,
                                                        self._p)
        elif self.minimizer in self._function_methods_with_jac:
            mysys = multiminimize.gsl_multimin_function_fdf(self._chi_squared,
                                                            self._jac_chi_squared,
                                                            self._chi_squared_fdf,
                                                            self._data,
                                                            self._p)
        else:
            raise RuntimeError("An undefined GSL minimizer was selected")
            
        # define the solver
        if self.minimizer=='lmsder':
            self._solver = multifit_nlin.lmsder(mysys, self._n, self._p)
        elif self.minimizer=='lmder':
            self._solver = multifit_nlin.lmder(mysys, self._n, self._p)
        elif self.minimizer=='simplex':
            self._solver = multiminimize.nmsimplex(mysys, self._p)
        elif self.minimizer=='simplex2':
            self._solver = multiminimize.nmsimplex2(mysys, self._p)
        elif self.minimizer=='conjugate_pr':
            self._solver = multiminimize.conjugate_pr(mysys, self._p)
        elif self.minimizer=='conjugate_fr':
            self._solver = multiminimize.conjugate_fr(mysys, self._p)
        elif self.minimizer=='bfgs':
            self._solver = multiminimize.bfgs(mysys, self._p)
        elif self.minimizer=='bfgs2':
            self._solver = multiminimize.bfgs2(mysys, self._p)
        elif self.minimizer=='steepest_descent':
            self._solver = multiminimize.steepest_descent(mysys, self._p)

        if self.minimizer in self._residual_methods:
            self._solver.set(self._pinit)
        elif self.minimizer in self._function_methods_no_jac:
            initial_steps = 0.1 * numx.array(np.ones(self._p))
            self._solver.set(self._pinit, initial_steps)
        else:
            self._solver.set(self._pinit, 0.01, 1e-4) # why magic numbers?

    def fit(self):
        """ 
        Run problem with GSL
        """
        self.success = False

        maxits   = 500  # consistent scipy/RALFit
        abserror = 1e-4 # consistent with Mantid
        relerror = 1e-4 # consistent with Mantid

        for iter in range(maxits):
            status = self._solver.iterate()
            # check if the method has converged
            if self.minimizer in self._residual_methods:
                x  = self._solver.getx()
                dx = self._solver.getdx()
                # check if we've converged
                status = multifit_nlin.test_delta(dx,x,abserror,relerror)
            elif self.minimizer in self._function_methods_no_jac:
                ssval = self._solver.size()
                status = multiminimize.test_size(ssval, 1e-2)
                # status is rval in sample code.  Break if rval=0.
                # is this Equivalent to status?
            else: # must be in function_methods_with_jac
                gradient = self._solver.gradient()
                status = multiminimize.test_gradient(gradient, 1e-3) #magic number                
            if status == errno.GSL_SUCCESS:
                self.success = True
                break
            elif status != errno.GSL_CONTINUE:
                raise ValueError("GSL couldn't find a solution")
        else:
            raise ValueError("Maximum number of iterations exceeded!")

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results 
        will be read from
        """
        if self.success:
            self.final_params = self._solver.getx()
            self.results = self.problem.eval_f(x=self.data_x,
                                               params=self.final_params,
                                               function_id=self.function_id)
            
        
