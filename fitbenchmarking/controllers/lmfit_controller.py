"""
Implements a controller for the Ceres fitting software.
"""
import sys
import os
import numpy as np
from lmfit import minimize, Parameters
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError


# class lmfit_resdiuals():
#     def __init__(self, fb_cf,initial_params,lmfit_p,params_names):
#         # MUST BE CALLED. Initializes the Ceres::CostFunction class
#         super().__init__()
#         self.fb_cf = fb_cf
#         self.initial_params = initial_params
#         self.lmfit_p = lmfit_p
#         self.params_names = params_names

#     def lmfit_resdiual (self,params):
#         """
#         """
#         p_ini = self.initial_params
#         self.lmfit_p = np.zeros(len(p_ini))
#         for i , name in enumerate(self.params_names):
#             self.lmfit_p[i] = params[name]
#             #print(type(self.lmfit_p.tolist()))
#             #print(len(self.initial_params))
#             p = self.lmfit_p.tolist()
#         if  len(p) ==  len(p_ini):
#             return self.fb_cf.eval_r(self.lmfit_p.tolist())

class LmfitController(Controller):
    """
    Controller for lmfit
    """

    algorithm_check = {
        'all': ['differential_evolution',
                'brute',
                'basinhopping',
                'powell',
                'cobyla',
                'slsqp',
                'emcee',
                'nelder',
                'least_squares',
                'trust-ncg',
                'trust-exact',
                'trust-krylov',
                'trust-constr',
                'dogleg',
                'leastsq',
                'newton',
                'tnc',
                'lbfgsb',
                'bfgs' ,
                'cg' ,
                'ampgo',
                'shgo',
                'dual_annealing'
                ],
        'ls': [],
        'deriv_free': ['differential_evolution',
                       'brute',
                       'basinhopping',
                       'powell',
                       'cobyla',
                       'slsqp',
                       'emcee',
                       ],
        'general': [],
        'simplex': ['nelder'],
        'trust_region': ['least_squares',
                         'trust-ncg',
                         'trust-exact',
                         'trust-krylov',
                         'trust-constr',
                         'dogleg'],
        'levenberg-marquardt': ['leastsq'],
        'gauss_newton': ['newton',
                         'tnc'],
        'bfgs': ['lbfgsb',
                 'bfgs'],
        'conjugate_gradient': ['cg'],
        'steepest_descent': [],
        'global_optimization': ['ampgo',
                                'shgo',
                                'dual_annealing']
        }


    #jacobian_enabled_solvers = ['lm-lsqr']


    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.result = []
        self._status = None
        self._popt = None
        self.lmfit_out = None
        self.lmfit_params = Parameters()
        self.lmfit_p = None
        #self.param_dict = None
        self.params_names = self.problem.param_names
        self.res = None

    def lmfit_resdiual (self,params):
        """
        """
        p_ini = self.initial_params
        self.lmfit_p = np.zeros(len(p_ini))
        for i , name in enumerate(self.params_names):
            self.lmfit_p[i] = params[name]
            #print(type(self.lmfit_p.tolist()))
            #print(len(self.initial_params))
            p = self.lmfit_p.tolist()
        if  len(p) ==  len(p_ini):
            return self.cost_func.eval_r(self.lmfit_p.tolist())
    def setup(self):
        """
        Setup problem ready to be run with Ceres solver
        """
        #self.res = lmfit_resdiuals(self.cost_func,self.initial_params,self.lmfit_p,self.params_names)
        
        for i ,names in enumerate(self.params_names):
            self.lmfit_params.add(names, value=self.initial_params[i])


        #print(self.param_dict)
        #print(self.lmfit_params)


    def fit(self):
        """
        Run problem with Ceres solver
        """
        

   
        self.lmfit_out = minimize(self.lmfit_resdiual, self.lmfit_params, method=self.minimizer)
 
        # for _, param in out.params.items():
        #       self.result.append(param.value)
        #self._status = 0 if "success" in self.kmpfit_object.message else 2


    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        if self._status == 0:
            self.flag = 0
        else:
            self.flag = 2
        
        for _, param in self.lmfit_out.params.items():
              self.result.append(param.value)

        self.final_params = self.result
        
        