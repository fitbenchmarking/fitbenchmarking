"""
Implements a controller for the CERN pacakage Minuit
https://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/
using the iminuit python interface
http://iminuit.readthedocs.org
"""
from iminuit import Minuit
import numpy as np

from fitbenchmarking.fitting.controllers.base_controller import Controller


class MinuitController(Controller):
    """
    Controller for the Minuit fitting software
    """

    def __init__(self, problem, use_errors):
        """
        Initializes variable used for temporary storage.
        """
        super(MinuitController, self).__init__(problem, use_errors)
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
        self._minuit_problem = Minuit.from_array_func(self.problem.eval_r_norm,
                                                      self.initial_params,
                                                      error=self._initial_step,
                                                      errordef=1)

    def fit(self):
        """
        Run problem with Minuit
        """
        self.success = False
        self._minuit_problem.migrad()  # run optimizer

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read fromm
        """
        self._popt = self._minuit_problem.np_values()
        self.success = (self._popt is not None)

        if self.success:
            self.results = self.problem.eval_f(params=self._popt)
            self.final_params = self._popt
