"""
Implements a controller for the CERN package Minuit
https://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/
using the iminuit python interface
http://iminuit.readthedocs.org
"""
from iminuit import Minuit
from iminuit import __version__ as iminuit_version
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingSoftwareError


class MinuitController(Controller):
    """
    Controller for the Minuit fitting software
    """

    algorithm_check = {
            'all': ['minuit'],
            'ls': [],
            'deriv_free': [],
            'general': ['minuit'],
            'simplex': [],
            'trust_region': [],
            'levenberg-marquardt': [],
            'gauss_newton': [],
            'bfgs': [],
            'conjugate_gradient': [],
            'steepest_descent': [],
            'global_optimization': []}

    def __init__(self, cost_func):
        """
        Initializes variable used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`

        """

        if int(iminuit_version[:1]) < 2:
            raise MissingSoftwareError('iminuit version {} is not supported, '
                                       'please upgrade to at least version '
                                       '2.0.0'.format(iminuit_version))

        super().__init__(cost_func)

        self.support_for_bounds = True
        self.param_ranges = None
        self._status = None
        self._popt = None
        self._initial_step = None
        self._minuit_problem = None

    def setup(self):
        """
        Setup for Minuit
        """
        # minuit requires an initial step size.
        # The docs say
        # "A good guess is a fraction of the initial
        #  fit parameter value, e.g. 10%
        #  (be careful when applying this rule-of-thumb
        #  when the initial parameter value is zero "
        self._initial_step = 0.1 * np.array(self.initial_params)
        # set small steps to something sensible(?)
        self._initial_step[self._initial_step < 1e-12] = 1e-12
        self._minuit_problem = Minuit(self.cost_func.eval_cost,
                                      self.initial_params)
        self._minuit_problem.errordef = 1
        self._minuit_problem.errors = self._initial_step

        # If parameter ranges have been set in problem, then set up bounds
        # option. For minuit, is a sequence of (lb,ub) pairs for each
        # parameter. None is used to denote no bound for a parameter.
        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            lb = [None if x == -np.inf else x for x in lb]
            ub = [None if x == np.inf else x for x in ub]
            self.param_ranges = list(zip(lb, ub))
        else:
            self.param_ranges = [(-np.inf, np.inf)]*len(self.initial_params)

        self._minuit_problem.limits = self.param_ranges

    def fit(self):
        """
        Run problem with Minuit
        """
        self._minuit_problem.migrad()  # run optimizer
        self._status = 0 if self._minuit_problem.valid else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        fmin = self._minuit_problem.fmin
        if self._status == 0:
            self.flag = 0
        elif fmin.has_reached_call_limit:
            self.flag = 1
        else:
            self.flag = 2

        self._popt = np.array(self._minuit_problem.values)
        self.final_params = self._popt
