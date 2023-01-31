"""
Implements a controller for the Ceres fitting software.
"""
import sys
import os
import numpy as np
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import UnknownMinimizerError
pyceres_location = os.environ["PYCERES_LOCATION"]
sys.path.insert(0, pyceres_location)

# pylint: disable=wrong-import-position,wrong-import-order
import PyCeres # noqa
# pylint: enable=wrong-import-position,wrong-import-order


class CeresCostFunction(PyCeres.CostFunction):
    """
    Cost function for Ceres solver
    """
    def __init__(self, fb_cf):
        # MUST BE CALLED. Initializes the Ceres::CostFunction class
        super().__init__()
        self.fb_cf = fb_cf

        # MUST BE CALLED. Sets the size of the residuals and parameters
        self.set_num_residuals(len(self.fb_cf.problem.data_x))
        self.set_parameter_block_sizes([len(self.fb_cf.problem.param_names)])

    # The CostFunction::Evaluate(...) virtual function implementation

    def Evaluate(self, parameters, residuals, jacobians):
        """
        Evaluate for Ceres solver
        """

        x = parameters[0]

        res = self.fb_cf.eval_r(x)

        if np.any(np.isinf(res)):
            return False

        np.copyto(residuals, res)

        if jacobians is not None:
            np.copyto(jacobians[0], np.ravel(self.fb_cf.jac_res(x)))

        return True


class CeresController(Controller):
    """
    Controller for Ceres Solver
    """

    algorithm_check = {
        'all': ['Levenberg_Marquardt',
                'Dogleg',
                'BFGS',
                'LBFGS',
                'steepest_descent',
                'Fletcher_Reeves',
                'Polak_Ribiere',
                'Hestenes_Stiefel'],
        'ls': ['Levenberg_Marquardt',
               'Dogleg',
               'BFGS',
               'LBFGS',
               'steepest_descent',
               'Fletcher_Reeves',
               'Polak_Ribiere',
               'Hestenes_Stiefel'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': ['Levenberg_Marquardt', 'Dogleg'],
        'levenberg-marquardt': [],
        'gauss_newton': [],
        'bfgs': ['BFGS', 'LBFGS'],
        'conjugate_gradient': ['Fletcher_Reeves',
                               'Polak_Ribiere',
                               'Hestenes_Stiefel'],
        'steepest_descent': ['steepest_descent'],
        'global_optimization': []
    }

    jacobian_enabled_solvers = ['Levenberg_Marquardt',
                                'Dogleg',
                                'BFGS',
                                'LBFGS',
                                'steepest_descent',
                                'Fletcher_Reeves',
                                'Polak_Ribiere',
                                'Hestenes_Stiefel']

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
        self._status = None
        self.ceres_problem = PyCeres.Problem()
        self.ceres_options = PyCeres.SolverOptions()
        self.ceres_summary = PyCeres.Summary()
        self.ceres_cost_func = CeresCostFunction(self.cost_func)

    def setup(self):
        """
        Setup problem ready to be run with Ceres solver
        """
        self.result = np.array(self.initial_params)

        self.ceres_problem.AddResidualBlock(self.ceres_cost_func, None,
                                            self.result)

        self.ceres_options.max_num_iterations = 10000

        if self.value_ranges is not None:
            for i, (value_ranges_lb, value_ranges_ub) in \
              enumerate(self.value_ranges):
                self.ceres_problem.SetParameterLowerBound(self.result,
                                                          i,
                                                          value_ranges_lb)
                self.ceres_problem.SetParameterUpperBound(self.result,
                                                          i,
                                                          value_ranges_ub)

        self.ceres_options.linear_solver_type = \
            PyCeres.LinearSolverType.DENSE_QR

        if self.minimizer == "Levenberg_Marquardt":
            self.ceres_options.trust_region_strategy_type =  \
                PyCeres.TrustRegionStrategyType.LEVENBERG_MARQUARDT
        elif self.minimizer == "Dogleg":
            self.ceres_options.trust_region_strategy_type = \
                PyCeres.TrustRegionStrategyType.DOGLEG
        elif self.minimizer == "BFGS":
            self.ceres_options.line_search_direction_type = \
                PyCeres.LineSearchDirectionType.BFGS
        elif self.minimizer == "LBFGS":
            self.ceres_options.line_search_direction_type = \
                PyCeres.LineSearchDirectionType.LBFGS
        elif self.minimizer == "steepest_descent":
            self.ceres_options.line_search_direction_type = \
                PyCeres.LineSearchDirectionType.STEEPEST_DESCENT
        elif self.minimizer == "Fletcher_Reeves":
            self.ceres_options.nonlinear_conjugate_gradient_type = \
                PyCeres.NonlinearConjugateGradientType.FLETCHER_REEVES
        elif self.minimizer == "Polak_Ribiere":
            self.ceres_options.nonlinear_conjugate_gradient_type = \
                PyCeres.NonlinearConjugateGradientType.POLAK_RIBIERE
        elif self.minimizer == "Hestenes_Stiefel":
            self.ceres_options.nonlinear_conjugate_gradient_type = \
                PyCeres.NonlinearConjugateGradientType.HESTENES_STIEFEL
        else:
            raise UnknownMinimizerError(
                f"No {self.minimizer} minimizer for Ceres solver")

    def fit(self):
        """
        Run problem with Ceres solver
        """

        PyCeres.Solve(self.ceres_options, self.ceres_problem,
                      self.ceres_summary)

        self._status = 0 if self.ceres_summary.IsSolutionUsable()  \
            else 2

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """

        if self._status == 0:
            self.flag = 0
        else:
            self.flag = 2

        self.final_params = self.result
