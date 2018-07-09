from __future__ import (absolute_import, division, print_function)

import unittest
import os

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from fitting_benchmarking import do_fitting_benchmark_one_problem
from fitting_benchmarking import prepare_wks_cost_function
from fitting_benchmarking import get_function_definitions
from fitting_benchmarking import run_fit
from fitting_benchmarking import SplitByString


class FitBenchmarkingOneProblemTest(unittest.TestCase):

    def test_prepare_wks_cost_function(self):


    def test_get_function_definitions(self):


    def test_run_fit(self):


    def test_SplitByString(self):


