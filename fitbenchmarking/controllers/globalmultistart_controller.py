"""
Implements a controller for global optimization algorithms.

Note: MS3 and linesearch are included here for testing only
"""
import numpy as np
import sys
sys.path.append("/home/upg88743/global-optimization/Multistart/")
from ms3 import ms3
from regularisation import regularisation
from linesearch import linesearch
from LBFGS_multistart import LBFGS

from scipy.optimize._numdiff import approx_derivative
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError

class globalmultistartController(Controller):
    """
    Controller for multistart global optimisation algorithms
    """

    def __init__(self,cost_func):
        """
        Initialise the class
        :param cost_func: Cost function object selected from options
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super(globalmultistartController,self).__init__(cost_func)
        self.support_for_bounds = True
        self._popt = None
        self.algorithm_check = {
            'all' : ['ms3','regularisation','linesearch','l_bfgs'],
            'ls' : [None],
            'deriv_free' : [None],
            'general' : ['ms3','regularisation','linesearch','l_bfgs'],
            'global_optimization' : ['ms3','regularisation','linesearch','l_bfgs']
        }

        self.jacobian_enabled_solvers = ['ms3','regularisation','linesearch','l_bfgs']

    def setup(self):
        """
        Setup problem ready to be run with ms3
        """
        self._options = {'k_max' : 200,
                    'l_max' : 100 ,
                    'eps' : 1e-4,
                    #'tau' : 0.1 #tau not used by regularisation algorithm
        }
        self._lbfgs = {'l_max' : 100
        }

        if self.value_ranges is None:
            raise MissingBoundsError("Multistart requires bounds on parameters")

        low, high = zip(*self.value_ranges)
        self._low = np.array(low)
        self._high = np.array(high)
        self._x0 = self.initial_params # store initial guess params

    def fit(self):
        """
        Run problem with MS3
        """
        # lower and upper bounds of the parameters to optimize
        xl = self._low
        xu = self._high

        # scaled upper and lower bounds
        yl = np.zeros_like(xl)
        yu = np.ones_like(xu)

        # number of dimensions of problem
        n = len(self._low)

        # Length of parameter blocks for alternating optimization
        self._n1 = 9 # All B parameters
        self._n2 = 6 # All shape parameters
        self._n = n # Number of parameters in total

        # No alternating optimization
        def R(y): return self.cost_func.eval_r(xl + (xu - xl)*y)
        def J(y): return approx_derivative(R,y,method=self.jacobian.method)

        # Alternating Optimization
        #     Consists of four stages:
        #     Stages 1 and 2 cover the first optimization pass
        #     Stages 3 and 4 cover the second optimization pass

        #Stage 1: Fix initial shape parameters, optimize B parameters
        def R1(y,n=self._n1):
            xk = np.concatenate( ((xl[:n] + (xu[:n]- xl[:n])*y[:n] ),self._x0[n:]))
            return self.cost_func.eval_r(xk)

        def J1(y,n=self._n1): return approx_derivative(R1,y,method=self.jacobian.method)

        #Stage 2: Fix optimized B parameters
        #         optimize shape params from initial guess
        def R2(y,n=self._n1):
            xk = np.concatenate( ( self._y1[:n], y[n:] ) )
            return self.cost_func.eval_r(xl + (xu - xl)*xk)

        def J2(y,n=self._n1): return approx_derivative(R2,y,method=self.jacobian.method)

       #Stage 3: Fix shape parameters, optimize B parameters
        def R3(y,n=self._n1):
            xk =  np.concatenate( (y[:n] ,self._y2[n:]))
            return self.cost_func.eval_r(xl + (xu - xl)*xk )

        def J3(y,n=self._n1): return approx_derivative(R3,y,method=self.jacobian.method)

        #Stage 4: Fix B parameters, optimize over shape parameters
        def R4(y,n=self._n1):
            xk = np.concatenate( ( self._y3[:n], y[n:] ) )
            return self.cost_func.eval_r(xl + (xu - xl)*xk)

        def J4(y,n=self._n1): return approx_derivative(R4,y,method=self.jacobian.method,rel_step=1e-5)

        # Optimization based on minimizer selected
        if self.minimizer == "ms3":
            xopt, status = ms3(self._n,R,J,self._low,self._high,**self._options)

        if self.minimizer == "regularisation":
            # Stage 1: Fix initial shape params, optimize B parameters
            n = self._n1
            yopt1, status = regularisation(self._n1,R1,J1,yl,yu,**self._options)
            x = np.concatenate((xl[:n] + (xu[:n] - xl[:n])*yopt1[:n],self._x0[n:]))
            x = (x - xl)/(xu-xl) # return to scaled bounds
            # Stage 2: Fix B parameters, optimize shape parameters
            self._y1 = x # we need these params so that we can fix the B params to optimize the shape params
            yopt2, status = regularisation(self._n2,R2,J2,yl,yu,alternate=x,**self._options)
            # Stage 3: Optimize over B parmeters again
            self._y2 = yopt2
            yopt3, status = regularisation(self._n1,R3,J3,yl,yu,alternate=yopt2,**self._options)
            self._y3 = yopt3
            # Stage 4: Optimize over shape parameters again
            yopt, status = regularisation(self._n2,R4,J4,yl,yu,alternate=yopt3,**self._options)
            xopt = xl + (xu - xl) * yopt

        if self.minimizer == "linesearch":
            yopt, status = linesearch(self._n,R,J,yl,yu,**self._options)
            xopt = xl + (xu - xl) * yopt

        if self.minimizer == "l_bfgs":
            yopt = LBFGS(R,J,yl,yu,**self._lbfgs)
            xopt = xl + (xu - xl) * yopt
            status = 0 # status fixed for testing

        self._popt = xopt
        self._status = status

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results will be read from
        """
        #print('cleanup')
        if self._status == 0:
            self.flag = 0
        elif self._status == 1:
            self.flag = 1
        else:
            self.flag = 3

        self.final_params = self._popt
        #print(self.final_params)
