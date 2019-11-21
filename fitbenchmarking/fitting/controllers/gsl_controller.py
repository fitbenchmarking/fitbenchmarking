"""
Implements a controller for GSL
https://www.gnu.org/software/gsl/
using the pyGSL python interface
https://sourceforge.net/projects/pygsl/
"""

import pygsl
from pygsl import multifit_nlin, errno
from pygsl import _numobj as numx

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

    
        
    def setup(self):
        """
        Setup for GSL
        """
        self._data = numx.array([self.data_x,
                                 self.data_y,
                                 self.data_e])
        self._n = len(self.data_x)
        self._p = len(self.initial_params)
        mysys = multifit_nlin.gsl_multifit_function_fdf(self._prediction_error,
                                                        self._jac,
                                                        self._fdf,
                                                        self._data,
                                                        self._n,
                                                        self._p)
        if self.minimizer=='lmsder':
            self._solver = multifit_nlin.lmsder(mysys, self._n, self._p)
        elif self.minimizer=='lmder':
            self._solver = multifit_nlin.lmder(mysys, self._n, self._p)
        else:
            raise RuntimeError("An undefined GSL minmizer was selected")
        self._pinit = numx.array(self.initial_params)
        self._solver.set(self._pinit)

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
            x  = self._solver.getx()
            dx = self._solver.getdx()
            # check if we've converged
            status = multifit_nlin.test_delta(dx,x,abserror,relerror)
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
            
        
