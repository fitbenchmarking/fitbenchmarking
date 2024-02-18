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

FITTING_DIR = "fitbenchmarking.core.fitting_benchmarking"


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


class FitbenchmarkingTests(unittest.TestCase):
    """
    Verifies the output of the Fit class when run with different options.
    """

    def setUp(self):
        """
        Sets up the class variables
        """
        self.root = os.getcwd()
        self.data_dir = self.root + \
            "/fitbenchmarking/benchmark_problems/NIST/average_difficulty/"

    def test_benchmarking_method_end_to_end(self):
        """
        The tests checks fitbenchmarking with the default software options.
        The /NIST/average_difficulty problem set is run with scipy_ls software.
        The results of running the new class are matched with the orginal
        benchmark function.
        """
        results_dir = self.root + "/fitbenchmarking/core/tests/expected.json"

        options = Options(additional_options={'software': ['scipy_ls']})

        cp = Checkpoint(options)
        fit = Fit(options=options,
                  data_dir=self.data_dir,
                  checkpointer=cp)
        results, failed_problems, unselected_minimizers = fit.benchmark()

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

    def test_perform_fit_method(self):
        """
        The tests checks __perform_fit method.
        Three /NIST/average_difficulty problem sets
        are run with 3 scipy software minimizers.
        """

        testcases = [{
                        'file': "ENSO.dat",
                        'results': [111.70773805099354,
                                    107.53453144913736,
                                    107.53120328018143]
                    },
                    {
                        'file': "Gauss3.dat",
                        'results': [76.64279628070524,
                                    76.65043476327958,
                                    77.82316923750186]
                    },
                    {
                        'file': "Lanczos1.dat",
                        'results': [0.0009937705466940194,
                                    0.06269418241377904,
                                    1.2886484184254505e-05]
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

                for minimizer, acc in zip(['Nelder-Mead', 'Powell', 'CG'],
                                          case['results']):

                    controller.minimizer = minimizer
                    accuracy, runtimes, emissions \
                        = fit._Fit__perform_fit(controller)

                    self.assertAlmostEqual(accuracy, acc, 6)
                    assert len(runtimes) == options.num_runs
                    assert emissions != np.inf

    def test_loop_over_hessians_method(self):
        """
        The tests checks __loop_over_hessians method.
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
        The tests checks __loop_over_jacobians method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
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
        The tests checks __loop_over_minimizers method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
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

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_minimizers",
           side_effect=mock_loop_over_minimizers_func_call)
    def test_fitbenchmarking_class_loop_over_software(self, mock):
        """
        The tests checks __loop_over_minimizers method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
        """

        data_file = self.data_dir + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy',
                                                           'scipy_ls']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)

        fit = Fit(options=options,
                  data_dir=data_file,
                  checkpointer=cp)

        results = fit._Fit__loop_over_fitting_software(cost_func)

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

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_fitting_software",
           side_effect=mock_loop_over_softwares_func_call)
    def test_fitbenchmarking_class_loop_over_cost_function(self, mock):
        """
        The tests checks __loop_over_minimizers method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
        """

        data_file = self.data_dir + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy'],
                                              'cost_func_type':
                                              ['nlls',
                                               'weighted_nlls']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()

        fit = Fit(options=options,
                  data_dir=data_file,
                  checkpointer=cp)

        results = fit._Fit__loop_over_cost_function(parsed_problem)

        assert len(results) == 18
        assert mock.call_count == 2
        assert all(isinstance(r, FittingResult) for r in results)
        assert isinstance(mock.call_args_list[0][0][0], NLLSCostFunc)
        assert isinstance(mock.call_args_list[1][0][0], WeightedNLLSCostFunc)

    @patch(f"{FITTING_DIR}.Fit._Fit__loop_over_cost_function",
           side_effect=mock_loop_over_cost_func_call)
    def test_fitbenchmarking_class_loop_over_starting_values(self, mock):
        """
        The tests checks __loop_over_minimizers method.
        Three /NIST/average_difficulty problem sets
        are run with 2 hessian methods.
        """

        data_file = self.data_dir + 'ENSO.dat'

        options = Options(additional_options={'software': ['scipy']})
        cp = Checkpoint(options)

        parsed_problem = parse_problem_file(data_file, options)
        parsed_problem.correct_data()

        fit = Fit(options=options,
                  data_dir=data_file,
                  checkpointer=cp)

        results = fit._Fit__loop_over_starting_values(parsed_problem)

        assert len(results) == 18
        assert mock.call_count == 2
        assert all(isinstance(r, FittingResult) for r in results)
