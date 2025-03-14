"""
Implements a controller for the paramonte software.
"""

import shutil

import numpy as np
import paramonte as pm

from fitbenchmarking.controllers.base_controller import Controller


class ParamonteController(Controller):
    """
    Controller for Paramonte
    """

    algorithm_check = {
        "all": ["paraDram_sampler"],
        "ls": [],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": [],
        "levenberg-marquardt": [],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": ["paraDram_sampler"],
    }

    support_for_bounds = True

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.result = None
        self.pmpd = pm.ParaDRAM()

    def setup(self):
        """
        Setup problem ready to be run with Paramonte
        """
        par_ini_p = self.initial_params
        param_dict = dict(zip(self.par_names, par_ini_p))

        # overwrite the existing output files just in case they already exist.
        self.pmpd.spec.overwriteRequested = True
        # specify the output file prefixes.
        self.pmpd.spec.outputFileName = (
            "./out_" + str(self.problem.name) + "/temp"
        )
        # set the output names of the parameters.
        self.pmpd.spec.variableNameList = self.par_names
        self.pmpd.spec.variableNameList = list(param_dict.keys())
        self.pmpd.spec.startPointVec = list(param_dict.values())
        self.pmpd.spec.chainSize = self.chain_length

        if self.value_ranges is not None:
            value_ranges_lb, value_ranges_ub = zip(*self.value_ranges)
            value_ranges_lb = [
                -10e20 if x == -np.inf else x for x in value_ranges_lb
            ]
            value_ranges_ub = [
                10e20 if x == np.inf else x for x in value_ranges_ub
            ]
            self.pmpd.spec.domainLowerLimitVec = value_ranges_lb
            self.pmpd.spec.domainUpperLimitVec = value_ranges_ub

    def fit(self):
        """
        Run problem with Paramonte
        """

        self.pmpd.runSampler(
            ndim=len(self.initial_params),
            getLogFunc=self.cost_func.eval_loglike,
        )

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        sample = self.pmpd.readSample(
            "./out_" + str(self.problem.name) + "/temp", renabled=True
        )[0]

        param = sample.df.mean()[1:]

        self.params_pdfs = sample.df.to_dict(orient="list")

        self.flag = 0

        self.final_params = list(param)

        shutil.rmtree("./out_" + str(self.problem.name) + "/")
