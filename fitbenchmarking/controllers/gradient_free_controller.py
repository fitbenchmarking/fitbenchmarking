"""
Implements a controller for Gradient Free Optimizers
"""

import gradient_free_optimizers as gfo
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingBoundsError


class GradientFreeController(Controller):
    """
    Controller for the Gradient Free Optimizers fitting software.
    """

    algorithm_check = {
        'all': ['HillClimbingOptimizer',
                'RepulsingHillClimbingOptimizer',
                'SimulatedAnnealingOptimizer',
                'RandomSearchOptimizer',
                'RandomRestartHillClimbingOptimizer',
                'RandomAnnealingOptimizer',
                'ParallelTemperingOptimizer',
                'ParticleSwarmOptimizer',
                'EvolutionStrategyOptimizer',
                'BayesianOptimizer',
                'TreeStructuredParzenEstimators',
                'DecisionTreeOptimizer'],
        'ls': [],
        'deriv_free': ['HillClimbingOptimizer',
                       'RepulsingHillClimbingOptimizer',
                       'SimulatedAnnealingOptimizer',
                       'RandomSearchOptimizer',
                       'RandomRestartHillClimbingOptimizer',
                       'RandomAnnealingOptimizer',
                       'ParallelTemperingOptimizer',
                       'ParticleSwarmOptimizer',
                       'EvolutionStrategyOptimizer',
                       'BayesianOptimizer',
                       'TreeStructuredParzenEstimators',
                       'DecisionTreeOptimizer'],
        'general': ['HillClimbingOptimizer',
                    'RepulsingHillClimbingOptimizer',
                    'SimulatedAnnealingOptimizer',
                    'RandomSearchOptimizer',
                    'RandomRestartHillClimbingOptimizer',
                    'RandomAnnealingOptimizer',
                    'ParallelTemperingOptimizer',
                    'ParticleSwarmOptimizer',
                    'EvolutionStrategyOptimizer',
                    'BayesianOptimizer',
                    'TreeStructuredParzenEstimators',
                    'DecisionTreeOptimizer'],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': [],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': ['HillClimbingOptimizer',
                                'RepulsingHillClimbingOptimizer',
                                'SimulatedAnnealingOptimizer',
                                'RandomSearchOptimizer',
                                'RandomRestartHillClimbingOptimizer',
                                'RandomAnnealingOptimizer',
                                'ParallelTemperingOptimizer',
                                'ParticleSwarmOptimizer',
                                'EvolutionStrategyOptimizer',
                                'BayesianOptimizer',
                                'TreeStructuredParzenEstimators',
                                'DecisionTreeOptimizer']}

    controller_name = 'gradient_free'

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = True
        self._status = None
        self.search_space = None
        self.initialize = None
        self.results = None

    def setup(self):
        """
        Setup for Gradient Free Optimizers
        """

        if self.value_ranges is None or np.any(np.isinf(self.value_ranges)):
            raise MissingBoundsError(
                "Gradient-Free-Optimizers requires finite bounds "
                "on all parameters")

        # set search_space to be the space where the minimizer can search
        # for the best parameters i.e. parameter bounds
        param_ranges = [np.arange(b[0], b[1], 0.1) for b in self.value_ranges]
        self.search_space = dict(zip(self.problem.param_names, param_ranges))

        # set dictionary of initial parameter values to pass to gfo search
        # function
        param_dict = {self.problem.param_names[i]: self.initial_params[i]
                      for i in range(len(self.initial_params))}

        self.initialize = {"warm_start": param_dict}

    def _feval(self, p):
        """
        Utility function to call cost_func.eval_cost with correct args

        :param p: parameters
        :type p: dict
        :return: result from cost_func.eval_cost
        :rtype: numpy array
        """

        # convert dictionary of parameter values to list
        p_list = [0] * len(self.problem.param_names)
        for v, n in enumerate(self.problem.param_names):
            p_list[v] = p[n]

        feval = -self.cost_func.eval_cost(p_list, x=self.data_x, y=self.data_y)
        return feval

    def fit(self):
        """
        Run problem with Gradient Free Optimizers
        """

        method_to_call = getattr(gfo, self.minimizer)

        opt = method_to_call(self.search_space)
        opt.search(self._feval, n_iter=1000, verbosity=False)
        self.results = opt.best_para
        self._status = 0 if self.results is not None else 1

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        self.final_params = [0] * len(self.problem.param_names)
        for v, n in enumerate(self.problem.param_names):
            self.final_params[v] = self.results[n]

        if self._status == 0:
            self.flag = 0
        else:
            self.flag = 2
