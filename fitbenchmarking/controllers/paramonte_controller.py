"""
Implements a controller for the paramonte.
"""

import paramonte as pm
import numpy as np
from scipy.stats import norm
from fitbenchmarking.controllers.base_controller import Controller


class ParamonteController(Controller):
    """
    Controller for Paramonte
    """

    algorithm_check = {
        'all': ['paraDram_sampler'],
        'ls': [],
        'deriv_free': [],
        'general': ['paraDram_sampler'],
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
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.support_for_bounds = True
        self.result = None
        self.pmpd = pm.ParaDRAM()

    def getLogLike(self, param):
        """
        Return the natural logarithm of the likelihood of observing the (X,Y)
        dataset defined globally outside of this function given the input
        parameter vector ``param``.

        Parameters
        ==========

            param
                A numpy 64-bit real vector containing the parameters of the
                model.

        Returns
        =======
            logLike
                The natural logarithm of the likelihood of observing the
                dataset  given ``param``.
        """

        loglikelihood = -1/2 * self.cost_func.eval_cost(param)

        return loglikelihood

    def setup(self):
        """
        Setup problem ready to be run with Paramonte
        """
        par_names = self.problem.param_names
        par_ini_p = self.initial_params
        param_dict = dict(zip(par_names, par_ini_p))

        # overwrite the existing output files just in case they already exist.
        self.pmpd.spec.overwriteRequested = True
        # specify the output file prefixes.
        self.pmpd.spec.outputFileName = "./out/temp"
        # set the random seed for the sake of reproducibity.
        self.pmpd.spec.randomSeed = 12345
        # set the output names of the parameters.
        self.pmpd.spec.variableNameList = par_names
        # set the number of uniquely sampled points from the likelihood 
        # function.
        self.pmpd.spec.chainSize = 20000
        self.pmpd.spec.adaptiveUpdateCount = 2*len(par_names)
        self.pmpd.spec.proposalModel = 'uniform'
        self.pmpd.spec.variableNameList = list(param_dict.keys())
        self.pmpd.spec.startPointVec = list(param_dict.values())
        self.pmpd.mpiEnabled = True

        if self.value_ranges is not None:
            value_ranges_lb, value_ranges_ub = zip(*self.value_ranges)
            self.pmpd.spec.domainLowerLimitVec = value_ranges_lb
            self.pmpd.spec.domainUpperLimitVec = value_ranges_ub

    def fit(self):
        """
        Run problem with Paramonte
        """

        self.pmpd.runSampler(ndim=len(self.initial_params),
                             getLogFunc=self.getLogLike)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        sample = self.pmpd.readSample("./out/temp", renabled=True)[0]

        param = sample.df.mean()[1:]

        self.flag = 0

        self.final_params = list(param)
