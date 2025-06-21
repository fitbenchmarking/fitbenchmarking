import numpy as np

from fitbenchmarking.controllers.base_controller import Controller

from fitit import fit, minimizers, Minimizer, Model
from fitit.cost_functions import MeanSquaredError
from fitit.framework.inspect import get_class_from_module


class FitItController(Controller):
    algorithm_check = {
        "all": [
            "GradientDescent",
            "GaussNewton",
            "LevenbergMarquardt",
        ],
        "ls": ["GaussNewton", "LevenbergMarquardt"],
        "deriv_free": [],
        "general": [
            "GradientDescent",
            "GaussNewton",
            "LevenbergMarquardt",
        ],
        "simplex": [],
        "trust_region": [],
        "levenberg-marquardt": ["LevenbergMarquardt"],
        "gauss_newton": ["GaussNewton"],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    jacobian_enabled_solvers = [
        "GradientDescent",
        "GaussNewton",
        "LevenbergMarquardt",
    ]

    support_for_bounds = False

    def __init__(self, cost_func):
        """
        Setup workspace, cost_function, ignore_invalid, and initialise vars
        used for temporary storage within the mantid controller

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self._fitit_model = None
        self._fitit_cost_function = None
        self._fitit_minimizer = None

        self._evaluator = None
        self._exit_code = None

    def setup(self) -> None:
        """
        Setup problem ready to run with FitIt.
        """
        class DerivedModel(Model):
            def evaluate(model_self, x, parameters):
                return self.problem.eval_model(x=x, params=parameters)

            def evaluate_jacobian(model_self, x, parameters):
                return self.problem.jacobian(x, parameters)

            def number_of_parameters(model_self) -> int:
                return len(self.initial_params)

        self._fitit_model = DerivedModel()
        self._fitit_cost_function = MeanSquaredError() # Not finished
        if self.minimizer is not None:
            self._fitit_minimizer = get_class_from_module(minimizers, Minimizer, self.minimizer)()

    def fit(self) -> None:
        """
        Run problem with FitIt.
        """
        evaluator, exit_code = fit(
            self.data_x,
            self.data_y,
            self._fitit_model,
            e=self.data_e,
            cost_function=self._fitit_cost_function,
            start_parameters=self.initial_params,
            minimizer=self._fitit_minimizer
        )

        self._evaluator = evaluator
        self._exit_code = exit_code

    def cleanup(self) -> None:
        """
        Convert the result to a numpy array and populate the variables results will be read from.
        """
        if self._exit_code.value in [0, 1, 7]:
            self.flag = self._exit_code.value
        else:
            self.flag = 2

        self.final_params = self._evaluator.final_parameters()
