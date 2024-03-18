"""
Tests for fitbenchmarking.core.fitting_benchmarking.Fit
"""
import os
import unittest
from unittest.mock import patch
import json
import numpy as np

from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.jacobian.analytic_jacobian import Analytic
from fitbenchmarking.core.fitting_benchmarking import Fit
from fitbenchmarking.cost_func.weighted_nlls_cost_func import (
    WeightedNLLSCostFunc)
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.exceptions import (FitBenchmarkException,
                                              IncompatibleCostFunctionError,
                                              UnsupportedMinimizerError,
                                              UnknownMinimizerError,
                                              IncompatibleMinimizerError,
                                              NoJacobianError,
                                              NoHessianError,
                                              ValidationException)

FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"
import inspect
from fitbenchmarking import benchmark_problems, test_files
TEST_FILES_DIR = os.path.dirname(inspect.getfile(test_files))
BENCH_PROB_DIR = os.path.dirname(inspect.getfile(benchmark_problems))
DATA_DIR = os.path.join(BENCH_PROB_DIR, 'NIST', 'average_difficulty')


def mock_loop_over_hessians_func_call(controller):
    """
    Mock function for the __loop_over_hessian method
    """
    result_args = {'controller': controller,
                   'accuracy': 1,
                   'runtimes': [2],
                   'emissions': 3,
                   'runtime_metric': 'mean'}
    result = FittingResult(**result_args)
    return [result]


def mock_loop_over_jacobians_func_call(controller):
    """
    Mock function for the __loop_over_jacobians method
    """
    controller.cost_func.jacobian = Analytic(controller.cost_func.problem)
    result = mock_loop_over_hessians_func_call(controller)
    return result


def mock_loop_over_minimizers_func_call(controller, minimizers):
    """
    Mock function for the __loop_over_minimizers method
    """
    results = []
    for _ in minimizers:
        result = mock_loop_over_jacobians_func_call(controller)
        results.extend(result)
    return results, []


def mock_loop_over_softwares_func_call(cost_func):
    """
    Mock function for the __loop_over_softwares method
    """
    controller = ScipyController(cost_func)
    controller.cost_func.jacobian = Analytic(controller.cost_func.problem)
    controller.parameter_set = 0
    results = []
    for _ in range(9):
        result = mock_loop_over_hessians_func_call(controller)
        results.extend(result)
    return results


def mock_loop_over_cost_func_call(problem):
    """
    Mock function for the __loop_over_cost_func method
    """
    cost_func = WeightedNLLSCostFunc(problem)
    results = mock_loop_over_softwares_func_call(cost_func)
    return results


def mock_loop_over_cost_func_call_all_fail(problem):
    """
    Mock function for the __loop_over_cost_func method
    """
    cost_func = WeightedNLLSCostFunc(problem)
    controller = ScipyController(cost_func)
    controller.cost_func.jacobian = Analytic(controller.cost_func.problem)
    controller.parameter_set = 0
    result = FittingResult(**{'controller': controller,
                              'accuracy': np.inf,
                              'runtimes': [2],
                              'emissions': 3,
                              'runtime_metric': 'mean'})
    return [result]


def mock_loop_over_starting_values(problem):
    """
    Mock function for the __loop_over_starting_values method
    """
    cost_func = WeightedNLLSCostFunc(problem)
    controller = ScipyController(cost_func)
    controller.cost_func.jacobian = Analytic(controller.cost_func.problem)
    controller.parameter_set = 0
    result = mock_loop_over_hessians_func_call(controller)
    return result


def set_up_controller(file, options):
    """
    Sets up the controller for the PerformFitTests
    """
    data_file = os.path.join(DATA_DIR, file)

    parsed_problem = parse_problem_file(data_file, options)
    parsed_problem.correct_data()
    cost_func = WeightedNLLSCostFunc(parsed_problem)

    controller = ScipyController(cost_func=cost_func)

    controller.cost_func.jacobian \
        = Analytic(controller.cost_func.problem)
    controller.parameter_set = 0

    return controller


class PerformFitTests(unittest.TestCase):
    """
    Verifies the output of the __perform_fit method
    in the Fit class when run with different options.
    """
    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        self.options = Options(additional_options={'software':
                                                   ['scipy']})
        self.cp = Checkpoint(self.options)

    def test_perform_fit_method(self):
        """
        The test checks __perform_fit method.
        Three /NIST/average_difficulty problem sets
        are run with 2 scipy software minimizers.
        """

        testcases = [{
                        'file': "ENSO.dat",
                        'results': [111.70773805099354,
                                    107.53453144913736]
                    },
                    {
                        'file': "Gauss3.dat",
                        'results': [76.64279628070524,
                                    76.65043476327958]
                    },
                    {
                        'file': "Lanczos1.dat",
                        'results': [0.0009937705466940194,
                                    0.06269418241377904]
                    }]

        for case in testcases:

            with self.subTest(case['file']):

                controller = set_up_controller(case['file'], self.options)

                fit = Fit(options=self.options,
                          data_dir='test',
                          checkpointer=self.cp)

                for minimizer, acc in zip(['Nelder-Mead', 'Powell'],
                                          case['results']):

                    controller.minimizer = minimizer
                    accuracy, runtimes, emissions \
                        = fit._Fit__perform_fit(controller)

                    self.assertAlmostEqual(accuracy, acc, 6)
                    assert len(runtimes) == self.options.num_runs
                    assert emissions != np.inf

    @patch("fitbenchmarking.controllers." +
           "base_controller.Controller.eval_confidence",
           return_value=2)
    def test_eval_confidence_branches(self, mock):
        """
        The test checks the eval_confidence branches in
        ___perform_fit method.
        """
        controller = set_up_controller("Gauss3.dat", self.options)

        controller.params_pdfs = 'None'
        controller.minimizer = 'Nelder-Mead'

        fit = Fit(options=self.options,
                  data_dir='test',
                  checkpointer=self.cp)
        accuracy, _, _ = fit._Fit__perform_fit(controller)
        assert accuracy == 0.5
        assert mock.call_count == 1

        controller.eval_confidence = 0
        accuracy, _, _ = fit._Fit__perform_fit(controller)
        assert accuracy == np.inf

    @patch("fitbenchmarking.controllers." +
           "base_controller.Controller.validate")
    def test_perform_fit_error_handling(self, mock):
        """
        The test checks ___perform_fit method
        handles Exceptions correctly.
        """
        controller = set_up_controller("Gauss3.dat", self.options)
        controller.minimizer = 'Nelder-Mead'

        fit = Fit(options=self.options,
                  data_dir='test',
                  checkpointer=self.cp)

        for exp in [ValidationException,
                    FitBenchmarkException]:
            mock.side_effect = exp
            accuracy, runtimes, emissions = \
                fit._Fit__perform_fit(controller)
            assert accuracy == np.inf
            assert emissions == np.inf
            assert runtimes == [np.inf] * 5

    @patch("timeit.Timer.repeat", return_value=[1, 1, 1, 1, 5])
    @patch("fitbenchmarking.controllers.scipy_controller." +
           "ScipyController.cleanup", return_value=None)
    @patch("fitbenchmarking.controllers.scipy_controller." +
           "ScipyController.check_attributes", return_value=None)
    def test_perform_fit_runtime_warning(self, mock1, mock2, mock3):
        """
        The test checks ___perform_fit method
        creates warning correctly when the time taken 
        by controller.execute increases too much across 
        runs (caching).
        """
        with warnings.catch_warnings(record=True) as w:
            controller = set_up_controller("ENSO.dat", self.options)
            controller.minimizer = 'Powell'

            fit = Fit(options=self.options,
                      data_dir='test4',
                      checkpointer=self.cp)

            _ = fit._Fit__perform_fit(controller)
            assert ("ratio of the max time to the min is 5.0"
                    in str(w[-1].message))
                    

    @patch("fitbenchmarking.controllers." +
           "base_controller.Controller.validate")
    def test_perform_fit_max_runtime_error(self, mock):
        """
        The test checks ___perform_fit method handles
        MaxRuntimeError correctly (i.e., sets controller.flag to 6).
        """
        controller = set_up_controller("Gauss3.dat", self.options)
        controller.minimizer = 'Nelder-Mead'

        fit = Fit(options=self.options,
                  data_dir='test5',
                  checkpointer=self.cp)

        mock.side_effect = MaxRuntimeError
        accuracy, runtimes, emissions = \
            fit._Fit__perform_fit(controller)
        assert controller.flag == 6
        assert accuracy == np.inf
        assert emissions == np.inf
        assert runtimes == [np.inf] * 5

    @patch("fitbenchmarking.controllers." +
           "base_controller.Controller.check_bounds_respected")
    def test_perform_fit_check_bounds_respected(self, mock):
        """
        The test checks ___perform_fit method checks the
        function 'check_bounds_respected' is called when the 
        problem has value ranges.
        """
        controller = set_up_controller("Gauss3.dat", self.options)
        controller.minimizer = 'Nelder-Mead'
        controller.problem.value_ranges = {'test': (0, 1)}
        fit = Fit(options=self.options,
                  data_dir='test6',
                  checkpointer=self.cp)
        _ = fit._Fit__perform_fit(controller)
        assert mock.call_count == 1

class HessianTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_hessians method
    in the Fit class when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        data_file = DATA_DIR + "Lanczos1.dat"

        options = Options(additional_options={'software': ['scipy'],
                                              'hes_method': ['analytic',
                                                             'default'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)

        self.controller = ScipyController(cost_func=cost_func)

        self.controller.cost_func.jacobian = \
            Analytic(self.controller.cost_func.problem)
        self.controller.parameter_set = 0
        self.controller.minimizer = 'Newton-CG'

        self.fit = Fit(options=options,
                       data_dir=data_file,
                       checkpointer=cp)

    @patch(f"{FITTING_DIR}.Fit._Fit__perform_fit",
           return_value=(1, 2, 3))
    def test_loop_over_hessians_method(self, mock):
        """
        The test checks __loop_over_hessians method.
        /NIST/average_difficulty problem set
        is run with 2 hessian methods.
        """
        results = self.fit._Fit__loop_over_hessians(self.controller)
        assert len(results) == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert mock.call_count == 2

    @patch(f"{FITTING_DIR}.Fit._Fit__perform_fit",
           return_value=(1, 2, 3))
    @patch("fitbenchmarking.hessian.scipy_hessian.Scipy.__init__")
    @patch("fitbenchmarking.hessian.analytic_hessian.Analytic.__init__")
    def test_loop_over_hessians_fallback(self,
                                         analytic,
                                         scipy,
                                         perform_fit):
        """
        The test checks __loop_over_hessians method
        handles fallback
        """
        analytic.side_effect = NoHessianError
        scipy.side_effect = NoHessianError
        results = self.fit._Fit__loop_over_hessians(self.controller)

        assert len(results) == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert (results[0].hess is None) and (results[1].hess is None)
        assert ((results[0].hessian_tag == '') and
                (results[1].hessian_tag == ''))
        assert perform_fit.call_count == 2

    @patch("fitbenchmarking.utils.fitbm_result.FittingResult")
    @patch(f"{FITTING_DIR}.Fit._Fit__perform_fit",
           return_value=([1, 1],
                         [2, 2],
                         [3, 3]))
    def test_loop_over_hessians_multifit(self, perform_fit, mock):
        """
        The test checks __loop_over_hessians method
        handles multfit
        """
        mock.return_value = FittingResult(**{
            'controller': self.controller,
            'accuracy': 1,
            'runtimes': [2],
            'emissions': 3,
            'runtime_metric': 'mean'})
        self.controller.problem.multifit = True
        self.controller.final_params = [None] * 2
        results = self.fit._Fit__loop_over_hessians(self.controller)
        assert len(results) == 4
        assert perform_fit.call_count == 2
        assert mock.call_count == 4

    @patch(f"{FITTING_DIR}.Fit._Fit__perform_fit",
           return_value=(1, 2, 3))
    def test_loop_over_hessians_minimizer_check(self,
                                                perform_fit):
        """
        The test checks __loop_over_hessians method
        handles minimizer check
        """
        self.controller.hessian_enabled_solvers = []
        results = self.fit._Fit__loop_over_hessians(self.controller)

        assert len(results) == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert (results[0].hess is None) and (results[1].hess is None)
        assert ((results[0].hessian_tag == '') and
                (results[1].hessian_tag == ''))
        assert perform_fit.call_count == 2


class JacobianTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_jacobians method
    in the Fit class when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        data_file = DATA_DIR + "Gauss3.dat"

        options = Options(additional_options={'software': ['scipy'],
                                              'hes_method': ['default'],
                                              'jac_method': ['analytic',
                                                             'default'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)

        self.controller = ScipyController(cost_func=cost_func)

        self.controller.parameter_set = 0
        self.controller.minimizer = 'Newton-CG'

        self.fit = Fit(options=options,
                       data_dir=data_file,
                       checkpointer=cp)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_hessians",
           side_effect=mock_loop_over_hessians_func_call)
    def test_loop_over_jacobians_methods(self, mock):
        """
        The test checks __loop_over_jacobians method.
        /NIST/average_difficulty problem set
        is run with 2 jacobian methods.
        """
        results = self.fit._Fit__loop_over_jacobians(self.controller)
        assert len(results) == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert [r.jac for r in results] == ['analytic', '']
        assert [r.jacobian_tag for r in results] == ['analytic', '']
        assert mock.call_count == 2

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_hessians")
    @patch("fitbenchmarking.jacobian.default_jacobian.Default.__init__")
    @patch("fitbenchmarking.jacobian.analytic_jacobian.Analytic.__init__")
    def test_loop_over_jacobians_fallback(self,
                                          analytic,
                                          default,
                                          loop_over_hessians):
        """
        The test checks __loop_over_jacobians method
        handles fallback correctly.
        """
        analytic.side_effect = NoJacobianError
        default.side_effect = NoJacobianError
        loop_over_hessians.side_effect = mock_loop_over_hessians_func_call

        results = self.fit._Fit__loop_over_jacobians(self.controller)

        assert len(results) == 1
        assert results[0].jac == 'scipy 2-point'
        assert results[0].jacobian_tag == 'scipy 2-point'

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_hessians")
    def test_loop_over_jacobians_stop_iteration_1(self,
                                                  loop_over_hessians):
        """
        The test checks __loop_over_jacobians method
        handles stop_iteration correctly.
        """
        loop_over_hessians.side_effect = mock_loop_over_hessians_func_call
        self.controller.jacobian_enabled_solvers = ['']
        results = self.fit._Fit__loop_over_jacobians(self.controller)
        assert len(results) == 1

    @patch("fitbenchmarking.jacobian.analytic_jacobian.Analytic.__init__")
    def test_loop_over_jacobians_stop_iteration_2(self,
                                                  analytic):
        """
        The test checks __loop_over_jacobians method
        handles stop_iteration correctly.
        """
        analytic.side_effect = StopIteration
        results = self.fit._Fit__loop_over_jacobians(self.controller)
        assert len(results) == 0


class MinimizersTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_minimizers method
    in the Fit class when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        data_file = DATA_DIR + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)

        self.controller = ScipyController(cost_func=cost_func)

        self.controller.parameter_set = 0

        self.fit = Fit(options=options,
                       data_dir=data_file,
                       checkpointer=cp)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_jacobians",
           side_effect=mock_loop_over_jacobians_func_call)
    def test_loop_over_minimizers(self, mock):
        """
        The test checks __loop_over_minimizers method.
        Enso.dat /NIST/average_difficulty problem set
        is run with 3 minimizers.
        """
        minimizers = ['Powell', 'CG', 'BFGS']
        results, minimizer_failed = \
            self.fit._Fit__loop_over_minimizers(self.controller, minimizers)
        assert len(results) == 3
        assert minimizer_failed == []
        assert [r.minimizer for r in results] == minimizers
        assert mock.call_count == 3
        assert all(isinstance(r, FittingResult) for r in results)

    @patch("fitbenchmarking.controllers.scipy_controller" +
           ".ScipyController.validate_minimizer")
    def test_unknown_minimizers_error(self, mock):
        """
        The test checks __loop_over_minimizers method
        handles UnknownMinimizerError correctly.
        """
        mock.side_effect = UnknownMinimizerError
        minimizers = ['Powell', 'CG', 'BFGS']
        results, minimizer_failed = \
            self.fit._Fit__loop_over_minimizers(self.controller, minimizers)
        assert len(results) == 0
        assert minimizer_failed == minimizers
        assert mock.call_count == 3

    @patch("fitbenchmarking.controllers.scipy_controller" +
           ".ScipyController.check_minimizer_bounds")
    def test_incompatible_minimizers_error_1(self, mock):
        """
        The test checks __loop_over_minimizers method.
        handles IncompatibleMinimizerError correctly.
        """
        mock.side_effect = IncompatibleMinimizerError
        self.controller.problem.value_ranges = '1'
        results, minimizer_failed = \
            self.fit._Fit__loop_over_minimizers(self.controller, ['Powell'])
        assert len(results) == 1
        assert results[0].runtime == np.inf
        assert minimizer_failed == []

    @patch("fitbenchmarking.cost_func.weighted_nlls_cost_func" +
           ".WeightedNLLSCostFunc.validate_algorithm_type")
    def test_incompatible_minimizers_error_2(self, mock):
        """
        The test checks __loop_over_minimizers method.
        handles IncompatibleMinimizerError correctly.
        """
        mock.side_effect = IncompatibleMinimizerError
        results, minimizer_failed = \
            self.fit._Fit__loop_over_minimizers(self.controller, ['Powell'])
        assert len(results) == 0
        assert minimizer_failed == ['Powell']


class SoftwareTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_software method
    in the Fit class when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        self.data_file = DATA_DIR + 'ENSO.dat'

        self.options = Options(additional_options={'software':
                                                   ['scipy',
                                                    'scipy_ls'],
                                                   'table_type':
                                                   ['acc',
                                                    'runtime',
                                                    'compare',
                                                    'local_min']})
        self.cp = Checkpoint(self.options)

        parsed_problem = parse_problem_file(self.data_file, self.options)
        parsed_problem.correct_data()
        self.cost_func = WeightedNLLSCostFunc(parsed_problem)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_minimizers",
           side_effect=mock_loop_over_minimizers_func_call)
    def test_loop_over_software(self, mock):
        """
        The test checks __loop_over_software method.
        Enso.dat /NIST/average_difficulty problem set
        is run with 2 softwares.
        """
        fit = Fit(options=self.options,
                  data_dir=self.data_file,
                  checkpointer=self.cp)

        results = fit._Fit__loop_over_fitting_software(self.cost_func)

        assert mock.call_count == 2
        assert mock.call_args_list[0][1]['minimizers'] == ['Nelder-Mead',
                                                           'Powell',
                                                           'CG',
                                                           'BFGS',
                                                           'Newton-CG',
                                                           'L-BFGS-B',
                                                           'TNC',
                                                           'SLSQP',
                                                           'COBYLA']
        assert mock.call_args_list[1][1]['minimizers'] == ['lm-scipy',
                                                           'trf',
                                                           'dogbox']
        assert len(results) == 12
        assert all(isinstance(r, FittingResult) for r in results)

    def test_loop_over_software_error(self):
        """
        The test checks __loop_over_software method.
        handles the UnsupportedMinimizerError correctly.
        """
        self.options.minimizers = {}
        fit = Fit(options=self.options,
                  data_dir=self.data_file,
                  checkpointer=self.cp)

        with self.assertRaises(UnsupportedMinimizerError) as _:
            fit._Fit__loop_over_fitting_software(self.cost_func)


class CostFunctionTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_cost_function method
    in the Fit class when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        data_file = DATA_DIR + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy'],
                                              'cost_func_type':
                                              ['nlls',
                                               'weighted_nlls'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)

        self.parsed_problem = parse_problem_file(data_file, options)
        self.parsed_problem.correct_data()

        self.fit = Fit(options=options,
                       data_dir=data_file,
                       checkpointer=cp)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_fitting_software",
           side_effect=mock_loop_over_softwares_func_call)
    def test_loop_over_cost_function(self, mock):
        """
        The test checks __loop_over_cost_function method.
        Enso.dat /NIST/average_difficulty problem set
        is run with 2 cost functions.
        """
        results = self.fit._Fit__loop_over_cost_function(self.parsed_problem)

        assert len(results) == 18
        assert mock.call_count == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert isinstance(mock.call_args_list[0][0][0], NLLSCostFunc)
        assert isinstance(mock.call_args_list[1][0][0], WeightedNLLSCostFunc)

    @patch("fitbenchmarking.cost_func.nlls_cost_func" +
           ".NLLSCostFunc.validate_problem")
    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_fitting_software",
           side_effect=mock_loop_over_softwares_func_call)
    def test_loop_over_cost_function_error(self,
                                           loop_over_fitting_software,
                                           mock):
        """
        The test checks __loop_over_cost_function method
        handles IncompatibleCostFunctionError correctly
        """
        mock.side_effect = IncompatibleCostFunctionError
        results = self.fit._Fit__loop_over_cost_function(self.parsed_problem)

        assert len(results) == 9
        assert loop_over_fitting_software.call_count == 1
        assert all(isinstance(r, FittingResult) for r in results)
        assert isinstance(loop_over_fitting_software.call_args_list[0][0][0],
                          WeightedNLLSCostFunc)


class StartingValueTests(unittest.TestCase):
    """
    Verifies the output of the __loop_over_starting_values method
    in the Fit class when run with different options.
    """
    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        data_file = DATA_DIR + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)

        self.parsed_problem = parse_problem_file(data_file, options)
        self.parsed_problem.correct_data()

        self.fit = Fit(options=options,
                       data_dir=data_file,
                       checkpointer=cp)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_cost_function",
           side_effect=mock_loop_over_cost_func_call)
    def test_loop_over_starting_values(self, mock):
        """
        The test checks __loop_over_starting_values method.
        Enso.dat /NIST/average_difficulty problem set is used.
        """
        results = self.fit._Fit__loop_over_starting_values(self.parsed_problem)

        assert len(results) == 18
        assert mock.call_count == 2
        assert all(isinstance(r, FittingResult) for r in results)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_cost_function",
           side_effect=mock_loop_over_cost_func_call_all_fail)
    def test_loop_over_starting_values_fail(self, mock):
        """
        The test checks that _failed_problems is updated correctly.
        """
        _ = self.fit._Fit__loop_over_starting_values(self.parsed_problem)

        assert self.fit._failed_problems == ['ENSO, Start 1', 'ENSO, Start 2']
        assert mock.call_count == 2


class BenchmarkTests(unittest.TestCase):
    """
    Verifies the output of the benchmarking method in the Fit class
    when run with different options.
    """

    def setUp(self):
        """
        Initializes the fit class for the tests
        """
        options = Options(additional_options={'software': ['scipy_ls'],
                                              'table_type': ['acc',
                                                             'runtime',
                                                             'compare',
                                                             'local_min']})
        cp = Checkpoint(options)
        self.fit = Fit(options=options,
                       data_dir=DATA_DIR,
                       checkpointer=cp)

    def test_benchmark_method(self):
        """
        This regression test checks fitbenchmarking with the default
        software options.The results of running the new class are matched
        with the orginal benchmark function. The /NIST/average_difficulty
        problem set is run with scipy_ls software.
        """
        results_dir = os.path.join(TEST_FILES_DIR, "regression_checkpoint.json")

        results, failed_problems, unselected_minimizers = self.fit.benchmark()

        # Import the expected results
        with open(results_dir) as j:
            expected = json.load(j)
            expected = expected['NIST_average_difficulty']

        # Verify none of the problems fail and no minimizers are unselected
        assert expected['failed_problems'] == failed_problems
        assert expected['unselected_minimizers'] == unselected_minimizers

        # Compare the results obtained with the expected results
        assert len(results) == len(expected['results'])
        for ix, r in enumerate(results):
            for attr in ['name',
                         'software',
                         'software_tag',
                         'minimizer',
                         'minimizer_tag',
                         'jacobian_tag',
                         'hessian_tag',
                         'costfun_tag']:
                assert r.__getattribute__(attr) == \
                    expected['results'][ix][attr]
            self.assertAlmostEqual(r.accuracy,
                                   expected['results'][ix]['accuracy'],
                                   6)
            assert r.hess == expected['results'][ix]['hessian']
            assert r.jac == expected['results'][ix]['jacobian']

    @patch(f"{FITTING_DIR}.parse_problem_file")
    @patch(f"{FITTING_DIR}.misc.get_problem_files",
           return_value=['problem_1', 'problem_2'])
    def test_benchmark_method_exp(self,
                                  get_problem_files,
                                  mock_parse_problem_file):
        """
        This test checks if FitBenchmarkException is caught
        during the method execution and no results are returned.
        """
        mock_parse_problem_file.side_effect = FitBenchmarkException
        results, failed_problems, _ = self.fit.benchmark()
        assert results == []
        assert failed_problems == []
        assert get_problem_files.call_count == 1
        assert mock_parse_problem_file.call_count == 2

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_starting_values",
           side_effect=mock_loop_over_starting_values)
    @patch(f"{FITTING_DIR}.misc.get_problem_files")
    def test_benchmark_method_repeat_name_handling(self,
                                                   mock_problem_files,
                                                   mock_starting_values):
        """
        This test checks that repeat problem manes are handles correctly
        """
        mock_problem_files.return_value = [DATA_DIR+'ENSO.dat'] * 2
        results, failed_problems, unselected_minimizers = self.fit.benchmark()
        assert len(results) == 2
        assert results[0].name == 'ENSO 1'
        assert results[1].name == 'ENSO 2'
        assert failed_problems == []
        assert unselected_minimizers == {}
        assert mock_starting_values.call_count == 2
        assert mock_problem_files.call_count == 1
