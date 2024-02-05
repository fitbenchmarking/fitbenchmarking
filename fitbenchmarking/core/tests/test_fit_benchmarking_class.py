"""
Tests for fitbenchmarking.core.fitting_benchmarking.Fit.__loop_over_fitting_software
"""
import inspect
import os
import unittest
from unittest.mock import Mock
import json

import numpy as np

from fitbenchmarking import test_files
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.core.fitting_benchmarking import Fit
from fitbenchmarking.cost_func.weighted_nlls_cost_func import WeightedNLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.exceptions import UnsupportedMinimizerError
from fitbenchmarking.utils.options import Options

class FitbenchmarkingTests(unittest.TestCase):
    """
    Verifies the output of the Fit class when run with different options. 
    """

    def setUp(self):
        """
        Setting up problem for tests
        """
        pass

    # def test_fitbenchmarking_end_to_end_with_scipy_ls_software(self):
    #     """
    #     The tests checks fitbenchmarking with the default software options.
    #     The /NIST/average_difficulty problem set is run with scipy_ls software.
    #     The results of running the new class are matched with the orginal
    #     benchmark function.
    #     """
    #     root = os.getcwd()
    #     data_dir = root + "/fitbenchmarking/benchmark_problems/NIST/average_difficulty"
    #     results_dir = root + "/fitbenchmarking/core/tests/expected.json"

    #     options = Options(additional_options={'software': ['scipy_ls']})

    #     cp = Checkpoint(options)
    #     fit = Fit(options=options,
    #               data_dir=data_dir,
    #               checkpointer=cp)
    #     results, failed_problems, unselected_minimizers = fit.benchmark()

    #     # Import the expected results
    #     with open(results_dir) as j:
    #         expected = json.load(j)
    #         expected = expected['NIST_average_difficulty']

    #     # Verify none of the problems fail and there are no unselected minimizers
    #     assert expected['failed_problems'] == failed_problems
    #     assert expected['unselected_minimizers'] == unselected_minimizers

    #     # Compare the results obtained with the expected results
    #     assert len(results) == len(expected['results'])
    #     for ix, r in enumerate(results):
    #         for attr in ['name',
    #                         'software',
    #                         'software_tag',
    #                         'minimizer',
    #                         'minimizer_tag',
    #                         'jacobian_tag',
    #                         'hessian_tag',
    #                         'costfun_tag',
    #                         'accuracy']:
    #             assert r.__getattribute__(attr) == expected['results'][ix][attr]
    #         assert r.hess == expected['results'][ix]['hessian']
    #         assert r.jac == expected['results'][ix]['jacobian']

    def test_fitbenchmarking_class_perform_fit(self):
        """
        The tests checks fitbenchmarking with the default software options.
        The /NIST/average_difficulty problem set is run with scipy software.
        The results of running the new class are matched with the orginal
        perform_fit function.
        """
        root = os.getcwd()
        data_dir = root + "/fitbenchmarking/benchmark_problems/NIST/average_difficulty/ENSO.dat"
        
        options = Options(additional_options={'software': ['scipy']})

        cp = Checkpoint(options)
        fit = Fit(options=options,
                  data_dir=data_dir,
                  checkpointer=cp)
        
        parsed_problem = parse_problem_file(data_dir, options)
        parsed_problem.correct_data()
        cost_func = WeightedNLLSCostFunc(parsed_problem)
    
        controller = ScipyController(cost_func=cost_func)

        controller.parameter_set = 0
        controller.minimizer = 'Nelder-Mead'

        accuracy, runtimes, emissions = fit._Fit__perform_fit(controller)

        assert accuracy == 111.70773805099354
        assert len(runtimes) == options.num_runs






        

                                          