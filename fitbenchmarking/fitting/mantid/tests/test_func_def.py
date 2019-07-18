from __future__ import (absolute_import, division, print_function)

import unittest
import os
import numpy as np
import mantid.simpleapi as msapi

from pathlib import *

import sys

data_prob_path = Path()
current_path = (Path(__file__).parts)
fb_dir_idx = current_path.index('fitbenchmarking')
data_prob_path = data_prob_path.joinpath(*current_path[:fb_dir_idx + 1])
main_path = data_prob_path.joinpath('fitbenchmarking')
sys.path.append(str(main_path))

from fitting.mantid.func_def import function_definitions
from fitting.mantid.func_def import parse_nist_function_definitions

from parsing.parse_nist_data import FittingProblem as NISTFittingProblem
from parsing.parse_fitbenchmark_data import FittingProblem as FBFittingProblem

class MantidTests(unittest.TestCase):

  def misra1a_file(self):
    """
    Helper function that returns the path to
    /fitbenchmarking/benchmark_problems
    """
    global data_prob_path
    file_path = data_prob_path
    file_path = file_path.joinpath('benchmark_problems',
                                             'Mock_Problem_Files', 'NIST_Misra1a.dat')

    fname = str(file_path)

    return fname

  def ENGINX_193749(self):
    """
    Helper function that returns the path to
    /fitbenchmarking/benchmark_problems
    """

      global data_prob_path
      file_path = data_prob_path
      file_path = file_path.joinpath('benchmark_problems',
                                               'Mock_Problem_Files',
                                               'FB_ENGINX193749_calibration_peak19.txt')

      fname = str(file_path)
      print(fname)

    return fname

  def NIST_problem(self):
    """
    Helper function.
    Sets up the problem object for the nist problem file Misra1a.dat
    """

    data_pattern = np.array([[10.07, 77.6],
                             [14.73, 114.9],
                             [17.94, 141.1],
                             [23.93, 190.8],
                             [29.61, 239.9],
                             [35.18, 289.0],
                             [40.02, 332.8],
                             [44.82, 378.4],
                             [50.76, 434.8],
                             [55.05, 477.3],
                             [61.01, 536.8],
                             [66.40, 593.1],
                             [75.47, 689.1],
                             [81.78, 760.0]])

    fname = self.misra1a_file()
    prob = NISTFittingProblem(fname)
    prob.name = 'Misra1a'
    prob.equation = 'b1*(1-exp(-b2*x))'
    prob.starting_values = [['b1', [500.0, 250.0]],
                            ['b2', [0.0001, 0.0005]]]
    prob.data_x = data_pattern[:, 1]
    prob.data_y = data_pattern[:, 0]

    return prob

  def Neutron_problem(self):
    """
    Sets up the problem object for the neutron problem file:
    ENGINX193749_calibration_peak19.txt
    """

    fname = self.ENGINX_193749()
    prob = FBFittingProblem(fname)
    prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
    prob.equation = ("name=LinearBackground,A0=0,A1=0;"
                     "name=BackToBackExponential,"
                     "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
    prob.starting_values = None
    prob.start_x = 23919.5789114
    prob.end_x = 24189.3183142

    return prob

  def create_wks_NIST_problem_with_errors(self):
    """
    Helper function.
    Creates a mantid workspace using the data provided by the
    NIST problem Misra1a.
    """

    prob = self.NIST_problem()
    data_e = np.sqrt(abs(prob.data_y))
    wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y,
                                    DataE=data_e)
    return wks_exp

  def create_wks_NIST_problem_without_errors(self):
    """
    Helper function.
    Creates a mantid workspace using the data provided by the
    NIST problem Misra1a.
    """

    prob = self.NIST_problem()
    wks_exp = msapi.CreateWorkspace(DataX=prob.data_x, DataY=prob.data_y)
    return wks_exp

  def test_functionDefinitions_return_NIST_functions(self):

    prob = self.NIST_problem()

    function_defs = function_definitions(prob)
    function_defs_expected = \
        ["name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=500.0,b2=0.0001",
         "name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=250.0,b2=0.0005"]

    self.assertListEqual(function_defs_expected, function_defs)

  def test_functionDefinitions_return_neutron_function(self):

    prob = self.Neutron_problem()

    function_defs = function_definitions(prob)
    function_defs_expected = \
        [("name=LinearBackground,A0=0,A1=0;name=BackToBackExponential,"
          "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")]

    self.assertListEqual(function_defs_expected, function_defs)

  def test_parseNistFunctionDefinitions_get_true_function(self):

    prob = self.NIST_problem()
    nb_start_vals = 2

    function_defs = parse_nist_function_definitions(prob, nb_start_vals)
    function_defs_expected = \
        ["name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=500.0,b2=0.0001",
         "name=UserFunction,Formula=b1*(1-exp(-b2*x)),b1=250.0,b2=0.0005"]

    self.assertListEqual(function_defs_expected, function_defs)


if __name__ == "__main__":
  unittest.main()
