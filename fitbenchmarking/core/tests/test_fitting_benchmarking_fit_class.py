"""
Tests for fitbenchmarking.core.fitting_benchmarking.Fit class
"""
import os
import unittest
from unittest.mock import MagicMock, patch
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
                                              UnsupportedMinimizerError)

FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"
ROOT = os.getcwd()
DATA_DIR = ROOT + \
    "/fitbenchmarking/benchmark_problems/NIST/average_difficulty/"


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


class FitbenchmarkingTests(unittest.TestCase):
    """
    Verifies the output of the Fit class when run with different options.
    """

    def setUp(self):
        """
        Sets up the directory variables
        """
        self.root = os.getcwd()
        self.data_dir = self.root + \
            "/fitbenchmarking/benchmark_problems/NIST/average_difficulty/"

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

                data_file = self.data_dir + case['file']

                options = Options(additional_options={'software': ['scipy']})
                cp = Checkpoint(options)

                parsed_problem = parse_problem_file(data_file, options)
                parsed_problem.correct_data()
                cost_func = WeightedNLLSCostFunc(parsed_problem)

                controller = ScipyController(cost_func=cost_func)

                controller.cost_func.jacobian \
                    = Analytic(controller.cost_func.problem)
                controller.parameter_set = 0

                fit = Fit(options=options,
                          data_dir=data_file,
                          checkpointer=cp)

                for minimizer, acc in zip(['Nelder-Mead', 'Powell'],
                                          case['results']):

                    controller.minimizer = minimizer
                    accuracy, runtimes, emissions \
                        = fit._Fit__perform_fit(controller)

                    self.assertAlmostEqual(accuracy, acc, 6)
                    assert len(runtimes) == options.num_runs
                    assert emissions != np.inf

    def test_loop_over_hessians_method(self):
        """
        The test checks __loop_over_hessians method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
        """

        for file in ["ENSO.dat", "Gauss3.dat", "Lanczos1.dat"]:

            data_file = self.data_dir + file

            options = Options(additional_options={'software': ['scipy'],
                                                  'hes_method': ['analytic',
                                                                 'default']})
            cp = Checkpoint(options)

            parsed_problem = parse_problem_file(data_file, options)
            parsed_problem.correct_data()
            cost_func = WeightedNLLSCostFunc(parsed_problem)

            controller = ScipyController(cost_func=cost_func)

            controller.cost_func.jacobian = \
                Analytic(controller.cost_func.problem)
            controller.parameter_set = 0
            controller.minimizer = 'Newton-CG'

            fit = Fit(options=options,
                      data_dir=data_file,
                      checkpointer=cp)

            fit._Fit__perform_fit = MagicMock()
            fit._Fit__perform_fit.return_value = (1, 2, 3)
            results = fit._Fit__loop_over_hessians(controller)

            assert len(results) == 2
            assert all(isinstance(r, FittingResult) for r in results)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_hessians",
           side_effect=mock_loop_over_hessians_func_call)
    def test_loop_over_jacobians_methods(self, mock):
        """
        The test checks __loop_over_jacobians method.
        Three /NIST/average_difficulty problem sets
        are run with 2 jacobian methods.
        """

        for file in ["ENSO.dat", "Gauss3.dat", "Lanczos1.dat"]:

            data_file = self.data_dir + file

            options = Options(additional_options={'software': ['scipy'],
                                                  'hes_method': ['default'],
                                                  'jac_method': ['analytic',
                                                                 'default']})
            cp = Checkpoint(options)

            parsed_problem = parse_problem_file(data_file, options)
            parsed_problem.correct_data()
            cost_func = WeightedNLLSCostFunc(parsed_problem)

            controller = ScipyController(cost_func=cost_func)

            controller.parameter_set = 0

            fit = Fit(options=options,
                      data_dir=data_file,
                      checkpointer=cp)

            controller.minimizer = 'Newton-CG'
            results = fit._Fit__loop_over_jacobians(controller)

            assert len(results) == 2
            assert all(isinstance(r, FittingResult) for r in results)
            assert [r.jac for r in results] == ['analytic', '']
            assert [r.jacobian_tag for r in results] == ['analytic', '']

        assert mock.call_count == 6

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_jacobians",
           side_effect=mock_loop_over_jacobians_func_call)
    def test_fitbenchmarking_class_loop_over_minimizers(self, mock):
        """
        The test checks __loop_over_minimizers method.
        Enso.dat /NIST/average_difficulty problem set
        is run with 3 minimizers.
        """

        data_file = self.data_dir + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)

        controller = ScipyController(cost_func=cost_func)

        controller.parameter_set = 0

        fit = Fit(options=options,
                  data_dir=data_file,
                  checkpointer=cp)

        minimizers = ['Powell', 'CG', 'BFGS']

        results, minimizer_failed = fit._Fit__loop_over_minimizers(controller,
                                                                   minimizers)

        assert len(results) == 3
        assert minimizer_failed == []
        assert [r.minimizer for r in results] == minimizers
        assert mock.call_count == 3
        assert all(isinstance(r, FittingResult) for r in results)


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

        self.options = Options(additional_options={'software': ['scipy',
                                                                'scipy_ls']})
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
                                               'weighted_nlls']})
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
    def test_loop_over_cost_function_error(self, mock, mock2):
        """
        The test checks __loop_over_cost_function method
        handles IncompatibleCostFunctionError correctly
        """
        mock2.side_effect = IncompatibleCostFunctionError
        results = self.fit._Fit__loop_over_cost_function(self.parsed_problem)

        assert len(results) == 9
        assert mock.call_count == 1
        assert all(isinstance(r, FittingResult) for r in results)
        assert isinstance(mock.call_args_list[0][0][0], WeightedNLLSCostFunc)


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

        options = Options(additional_options={'software': ['scipy']})
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
        options = Options(additional_options={'software': ['scipy_ls']})
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
        results_dir = ROOT + \
            "/fitbenchmarking/test_files/regression_checkpoint.json"

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
