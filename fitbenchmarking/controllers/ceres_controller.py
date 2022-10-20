"""
Implements a controller for the Ceres fitting software.
"""
import sys
import os
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
    def __init__(self):
        # MUST BE CALLED. Initializes the Ceres::CostFunction class
        super().__init__()

        # MUST BE CALLED. Sets the size of the residuals and parameters
        self.set_num_residuals(1)
        self.set_parameter_block_sizes([1])

        # Used to check whether the algorithm type of the
        # selected minimizer is incompatible with the cost function

        self.invalid_algorithm_types = ['ls']

    # The CostFunction::Evaluate(...) virtual function implementation

    # pylint: disable=no-self-use
    def Evaluate(self, parameters, residuals, jacobians):
        """
        Evaluate for Ceres solver
        """
        x = parameters[0][0]

        residuals[0] = 10 - x

        if jacobians is not None:  # check for Null
            jacobians[0][0] = -1

        return True
    # pylint: enable=no-self-use


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
        self.result = None
        self._status = None
        self._popt = None
        self.ceres_problem = PyCeres.Problem()
        self.ceres_options = PyCeres.SolverOptions()
        self.ceres_summary = PyCeres.Summary()
        self.ceres_cost_func = CeresCostFunction()

    def setup(self):
        """
        Setup problem ready to be run with Ceres solver
        """
        self.result = self.initial_params
        print("intial results", self.result)

        self.ceres_problem.AddResidualBlock(self.ceres_cost_func, None,
                                            self.result)

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
                "No {} minimizer for Ceres solver".format(self.minimizer))

        self.ceres_options.minimizer_progress_to_stdout = True

    def fit(self):
        """
        Run problem with Ceres solver
        """
        # Here we create the problem as in normal Ceres00

        PyCeres.Solve(self.ceres_options, self.ceres_problem,
                      self.ceres_summary)

        self.result = self.initial_params

        self._status = 0 if self.ceres_summary.IsSolutionUsable() is True \
            else 1

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
