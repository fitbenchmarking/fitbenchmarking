"""
Implements a controller for the CERN pacakage Minuit
https://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/
using the iminuit python interface
http://iminuit.readthedocs.org
"""
from iminuit import Minuit
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class MinuitController(Controller):
    """
    Controller for the Minuit fitting software
    """

    def __init__(self, problem):
        """
        Initializes variable used for temporary storage.

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(MinuitController, self).__init__(problem)
        self._popt = None
        self._initial_step = None
        self._minuit_problem = None
        self.algorithm_check = {
            'all': ['minuit'],
            'ls': [None],
            'deriv_free': [None],
            'general': ['minuit']}

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
        self._minuit_problem = Minuit.from_array_func(self.problem.eval_r_norm,
                                                      self.initial_params,
                                                      error=self._initial_step,
                                                      errordef=1)

    def fit(self):
        """
        Run problem with Minuit
        """
        self._minuit_problem.migrad()  # run optimizer
        self._status = 0 if self._minuit_problem.migrad_ok() else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        fmin = self._minuit_problem.get_fmin()
        if self._status == 0:
            self.flag = 0
        elif fmin.has_reached_call_limit:
            self.flag = 1
        else:
            self.flag = 2

        self._popt = self._minuit_problem.np_values()
        self.final_params = self._popt
