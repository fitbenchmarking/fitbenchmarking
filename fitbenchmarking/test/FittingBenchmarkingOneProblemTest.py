from __future__ import (absolute_import, division, print_function)

import unittest
import os
import mantid.simpleapi as msapi
import numpy as np

# DELETE RELATIVE PATH WHEN GIT TESTS ARE ENABLED
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from fitting_benchmarking import do_fitting_benchmark_one_problem
from fitting_benchmarking import prepare_wks_cost_function
from fitting_benchmarking import get_function_definitions
from fitting_benchmarking import run_fit
from fitting_benchmarking import splitByString
import test_result
import test_problem

# Note for readability: all tests follow the same structure, i.e. :
# setting up expected results
# calculating the actual results
# comparing the two
# Each of these sections is delimited by an empty new line.

class FittingBenchmarkingOneProblem(unittest.TestCase):

    def EnginxDataPath(self):
        ''' Helper function that returns the path ../benchmark_problems/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        enginxData_path = os.path.join(bench_prob_dir, 'Neutron_data','data_files',
                                       'ENGINX193749_calibration_spec651.nxs')

        return enginxData_path


    def NeutronProblem(self):
        ''' Sets up the problem object for the neutron problem file:
            ENGINX193749_calibration_peak19.txt '''

        enginxData_path = self.EnginxDataPath()

        prob = test_problem.FittingTestProblem()
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.equation = ("name=LinearBackground;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

        wks = msapi.Load(Filename= enginxData_path)
        prob.data_pattern_in = wks.readX(0)
        prob.data_pattern_out = wks.readY(0)
        prob.data_pattern_obs_errors = wks.readE(0)
        prob.ref_residual_sum_sq = 0

        return prob


    def NeutronProblemReferenceFitWks(self):
        ''' The fit workspace obtained manually through mantidplot for the
            neutron problem file ENGINX193749_calibration_peak19.txt with
            the neutron data file ENGINX193749_calibration_spec651.nxs '''

        # This fit workspace was obtained in MantidPlot v3.12.1
        current_dir = os.path.dirname(os.path.realpath(__file__))
        mock_problems_dir = os.path.join(current_dir, 'mock_problems')
        reference_fit_wks_path = os.path.join(mock_problems_dir, 'data_files',
                                              'fitWorkspace_enginxPeak19.nxs')

        return reference_fit_wks_path


    def NeutronProblemMock(self):
        ''' Sets up the problem object for the neutron problem file:
            ENGINX193749_calibration_peak19.txt with mock data entires'''

        prob = test_problem.FittingTestProblem()

        # These are actual entries:
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.equation = ("name=LinearBackground;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

        # These are mock entries, to avoid using Load
        prob.data_pattern_in = np.arange(10)
        prob.data_pattern_out = 100*np.arange(9)
        prob.data_pattern_obs_errors = np.sqrt(prob.data_pattern_out)
        prob.ref_residual_sum_sq = 0

        return prob


    def NISTproblem(self):
        ''' Sets up the problem object for the nist problem file Misra1a.dat '''

        data_pattern = np.array([ [10.07, 77.6],
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
                                  [81.78, 760.0] ])

        prob = test_problem.FittingTestProblem()
        prob.name = 'Misra1a.dat'
        prob.linked_name = ("`Misra1a.dat <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/misra1a.dat.shtml>`__")
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_pattern_in = data_pattern[:, 1:]
        prob.data_pattern_out = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894E-01

        return prob


    def test_do_fitting_benchmark_one_problem_neutron(self):

        prob = self.NeutronProblem()

        result_expected = test_result.FittingTestResult()
        result_expected.problem = prob
        result_expected.fit_status = 'success'
        result_expected.fit_chi2 = 0.79243138659204992
        result_expected.params = [-39.664909893833943, 0.0017093221460772121,
                                  620.29942532225425, 4.9265006277221284,
                                  0.030925377035352437, 24004.503970283724,
                                  13.856560250253684]
        result_expected.errors = [77.066145704360949, 0.003207694697161955,
                                  109.83586635802421, 204.44335838153586,
                                  0.018928810783550146, 16.399502434549809,
                                  6.2850091287092127]
        result_expected.sum_err_sq = 358.49892508988262

        minimizers = ['Levenberg-Marquardt']
        use_errors = True
        count = 0
        previous_name = "none"
        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                  count, previous_name)

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertEqual(result_expected.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result_expected.sum_err_sq, result.sum_err_sq)
        self.assertListEqual(result_expected.params, result.params)
        self.assertListEqual(result_expected.errors, result.errors)


    def test_do_fitting_benchmark_one_problem_nist(self):

        prob = self.NISTproblem()

        result1_expected = test_result.FittingTestResult()
        result1_expected.problem = prob
        result1_expected.fit_status = 'success'
        result1_expected.fit_chi2 = 3.0142776470113924e-05
        result1_expected.params = [234.06483564181511, 0.0005635749331078056]
        result1_expected.errors = [486.46049489836878, 0.0013377443749239895]
        result1_expected.sum_err_sq = 0.159784541

        result2_expected = test_result.FittingTestResult()
        result2_expected.problem = prob
        result2_expected.fit_status = 'success'
        result2_expected.fit_chi2 = 3.0142776474075721e-05
        result2_expected.params = [234.0648164895841, 0.00056357498391696424]
        result2_expected.errors = [486.46041069760378, 0.0013377443887498521]
        result2_expected.sum_err_sq = 0.159784814


        minimizers = ['Levenberg-Marquardt']
        use_errors = True
        count = 0
        previous_name = "none"
        results = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                   count, previous_name)


        result = results[0][0]
        self.assertEqual(result1_expected.problem, result.problem)
        self.assertEqual(result1_expected.fit_status, result.fit_status)
        self.assertAlmostEqual(result1_expected.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result1_expected.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result1_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(result1_expected.params[1],result.params[1])
        self.assertAlmostEqual(result1_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result1_expected.errors[1],result.errors[1])

        result = results[1][0]
        self.assertEqual(result2_expected.problem, result.problem)
        self.assertEqual(result2_expected.fit_status, result.fit_status)
        self.assertAlmostEqual(result2_expected.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result2_expected.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result2_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(result2_expected.params[1],result.params[1])
        self.assertAlmostEqual(result2_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result2_expected.errors[1],result.errors[1])


    def test_do_fitting_benchmark_one_problem_mantidFit_fails(self):

        prob = self.NeutronProblemMock()
        result_expected = test_result.FittingTestResult()
        result_expected.problem = prob
        result_expected.fit_status = 'failed'
        result_expected.fit_chi2 = np.nan
        result_expected.params = np.nan
        result_expected.errors = np.nan
        result_expected.sum_err_sq = np.nan

        minimizers = ['Levenberg-Marquardetss']
        use_errors = True
        count = 0
        previous_name = "none"
        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                  count, previous_name)

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        np.testing.assert_equal(result_expected.fit_chi2, result.fit_chi2)
        np.testing.assert_equal(result_expected.sum_err_sq, result.sum_err_sq)
        np.testing.assert_equal(result_expected.params, result.params)
        np.testing.assert_equal(result_expected.errors, result.errors)


    def test_run_fit(self):

        reference_fit_wks_path = self.NeutronProblemReferenceFitWks()
        fit_wks_expected = msapi.Load(reference_fit_wks_path)
        status_expected = 'success'
        chi2_expected = 0.79243138659204992
        params_expected = [-39.664909893833943, 0.0017093221460772121,
                         620.29942532225425, 4.9265006277221284,
                         0.030925377035352437, 24004.503970283724,
                         13.856560250253684]
        errors_expected = [77.066145704360949, 0.003207694697161955,
                         109.83586635802421, 204.44335838153586,
                         0.018928810783550146, 16.399502434549809,
                         6.2850091287092127]

        prob = self.NeutronProblem()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'
        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)

        self.assertEqual(status_expected, status)
        self.assertEqual(chi2_expected, chi2)
        self.assertListEqual(params_expected, params)
        self.assertListEqual(errors_expected, errors)
        result, messages = msapi.CompareWorkspaces(fit_wks_expected, fit_wks)
        self.assertTrue(result)


    def test_run_fit_mantidFit_fails(self):

        status_expected = 'failed'
        chi2_expected = np.nan
        fit_wks_expected = np.nan
        params_expected = np.nan
        errors_expected = np.nan

        prob = self.NeutronProblemMock()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Merquardtss'
        cost_function = 'Least squared'
        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)

        self.assertEqual(status_expected, status)
        np.testing.assert_equal(chi2_expected, chi2)
        np.testing.assert_equal(params_expected, params)
        np.testing.assert_equal(errors_expected, errors)
        np.testing.assert_equal(fit_wks_expected, fit_wks)


    def test_prepare_wks_cost_function(self):

        # Test when use_errors is True and obs_errors is a numpy arrray
        prob = self.NeutronProblemMock()
        data_e = prob.data_pattern_obs_errors
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out,
                                             DataE=data_e)
        cost_function_expected = 'Least squares'

        use_errors = True
        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


        # Test when use_errors is False
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out)
        cost_function_expected = 'Unweighted least squares'

        use_errors = False
        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


        # Test when use_errors is True and obs_errors is not a numpy arrray
        prob = self.NISTproblem()
        data_e = np.sqrt(prob.data_pattern_in)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out,
                                             DataE=data_e)
        cost_function_expected = 'Least squares'

        use_errors = True
        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_get_function_definitions(self):

        # Test when prob.starting_values = None
        prob = self.NeutronProblemMock()
        function_defs_expected = [prob.equation]

        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs_expected, function_defs)


        # Test when prob.starting_values = to something
        function_defs_expected = ["name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                  "b1=500.0,b2=0.0001,",
                                  "name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                  "b1=250.0,b2=0.0005," ]

        prob = self.NISTproblem()
        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs_expected, function_defs)


    def test_splitByString(self):

        # Test first if then if
        string_expected = "..."
        name = "Irrelevant"
        min_length = 5
        loop = 4
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_expected, string)

        # Test first if then else
        string_expected = "..."
        name = "TestStringRelevant"
        min_length = 5
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_expected, string)

        # Test second if directly to return name
        string_expected = "TestStringRelevant"
        name = "TestStringRelevant"
        min_length = 10
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_expected, string)

        # Test second if then if
        string_expected = "TestString;\nRelevant"
        name = "TestString;Relevant"
        min_length = 5
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_expected, string)

        string_expected = "TestString;\nRelevant"
        name = "TestString;Relevant"
        min_length = 10
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_expected, string)


if __name__ == "__main__":
    unittest.main()
