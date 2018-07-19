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

        # Obtained in mantid v3.12.1
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

        data_pattern = [ [10.07, 77.6],
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
                         [81.78, 760.0] ]
        data_pattern = np.asarray(data_pattern)

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

        result_actual = test_result.FittingTestResult()
        result_actual.problem = prob
        result_actual.fit_status = 'success'
        result_actual.fit_chi2 = 0.79243138659204992
        result_actual.params = [-39.664909893833943, 0.0017093221460772121,
                                620.29942532225425, 4.9265006277221284,
                                0.030925377035352437, 24004.503970283724,
                                13.856560250253684]
        result_actual.errors = [77.066145704360949, 0.003207694697161955,
                                109.83586635802421, 204.44335838153586,
                                0.018928810783550146, 16.399502434549809,
                                6.2850091287092127]
        result_actual.sum_err_sq = 358.49892508988262

        minimizers = ['Levenberg-Marquardt']
        use_errors = True
        count = 0
        previous_name = "none"
        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                  count, previous_name)
        result = result[0][0]
        self.assertEqual(result_actual.problem, result.problem)
        self.assertEqual(result_actual.fit_status, result.fit_status)
        self.assertEqual(result_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result_actual.sum_err_sq, result.sum_err_sq)
        self.assertListEqual(result_actual.params, result.params)
        self.assertListEqual(result_actual.errors, result.errors)


    def test_do_fitting_benchmark_one_problem_nist(self):

        prob = self.NISTproblem()

        result1_actual = test_result.FittingTestResult()
        result1_actual.problem = prob
        result1_actual.fit_status = 'success'
        result1_actual.fit_chi2 = 3.0142776470113924e-05
        result1_actual.params = [234.06483564181511, 0.0005635749331078056]
        result1_actual.errors = [486.46049489836878, 0.0013377443749239895]
        result1_actual.sum_err_sq = 0.159784541

        result2_actual = test_result.FittingTestResult()
        result2_actual.problem = prob
        result2_actual.fit_status = 'success'
        result2_actual.fit_chi2 = 3.0142776474075721e-05
        result2_actual.params = [234.0648164895841, 0.00056357498391696424]
        result2_actual.errors = [486.46041069760378, 0.0013377443887498521]
        result2_actual.sum_err_sq = 0.159784814

        minimizers = ['Levenberg-Marquardt']
        use_errors = True
        count = 0
        previous_name = "none"
        results = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                   count, previous_name)

        result = results[0][0]
        self.assertEqual(result1_actual.problem, result.problem)
        self.assertEqual(result1_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(result1_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result1_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result1_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(result1_actual.params[1],result.params[1])
        self.assertAlmostEqual(result1_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result1_actual.errors[1],result.errors[1])

        result = results[1][0]
        self.assertEqual(result2_actual.problem, result.problem)
        self.assertEqual(result2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(result2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(result2_actual.params[1],result.params[1])
        self.assertAlmostEqual(result2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result2_actual.errors[1],result.errors[1])

    def test_do_fitting_benchmark_one_problem_mantidFit_fails(self):

        prob = self.NeutronProblemMock()

        result_actual = test_result.FittingTestResult()
        result_actual.problem = prob
        result_actual.fit_status = 'failed'
        result_actual.fit_chi2 = np.nan
        result_actual.params = np.nan
        result_actual.errors = np.nan
        result_actual.sum_err_sq = np.nan

        minimizers = ['Levenberg-Marquardetss']
        use_errors = True
        count = 0
        previous_name = "none"
        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                  count, previous_name)

        result = result[0][0]
        self.assertEqual(result_actual.problem, result.problem)
        self.assertEqual(result_actual.fit_status, result.fit_status)
        self.assertTrue(np.testing.assert_equal(result_actual.fit_chi2, result.fit_chi2) is None)
        self.assertTrue(np.testing.assert_equal(result_actual.sum_err_sq, result.sum_err_sq) is None)
        self.assertTrue(np.testing.assert_equal(result_actual.params, result.params) is None)
        self.assertTrue(np.testing.assert_equal(result_actual.errors, result.errors) is None)


    def test_run_fit(self):

        reference_fit_wks_path = self.NeutronProblemReferenceFitWks()
        fit_wks_actual = msapi.Load(reference_fit_wks_path)
        status_actual = 'success'
        chi2_actual = 0.79243138659204992
        params_actual = [-39.664909893833943, 0.0017093221460772121,
                         620.29942532225425, 4.9265006277221284,
                         0.030925377035352437, 24004.503970283724,
                         13.856560250253684]
        errors_actual = [77.066145704360949, 0.003207694697161955,
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

        self.assertEqual(status_actual,status)
        self.assertEqual(chi2_actual,chi2)
        self.assertListEqual(params_actual,params)
        self.assertListEqual(errors_actual,errors)
        result, messages = msapi.CompareWorkspaces(fit_wks_actual, fit_wks)
        self.assertTrue(result)


    def test_run_fit_mantidFit_fails(self):

        status_actual = 'failed'
        chi2_actual = np.nan
        fit_wks_actual = np.nan
        params_actual = np.nan
        errors_actual = np.nan

        prob = self.NeutronProblemMock()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Merquardtss'
        cost_function = 'Least squared'
        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)

        self.assertEqual(status_actual,status)
        self.assertTrue(np.testing.assert_equal(chi2_actual,chi2) is None)
        self.assertTrue(np.testing.assert_equal(params_actual,params) is None)
        self.assertTrue(np.testing.assert_equal(errors_actual,errors) is None)
        self.assertTrue(np.testing.assert_equal(fit_wks_actual, fit_wks) is None)


    def test_prepare_wks_cost_function(self):

        prob = self.NeutronProblemMock()

        # Test when use_errors is True and obs_errors is a numpy arrray
        use_errors = True
        data_e = prob.data_pattern_obs_errors
        wks_actual = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                           DataY=prob.data_pattern_out,
                                           DataE=data_e)
        cost_function_actual = 'Least squares'

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_actual, wks)
        self.assertTrue(result, msg=("Failed at use_errors = True and "
                                     "obs_errors is a numpy array"))
        self.assertEqual(cost_function_actual, cost_function,
                         msg=("Failed at use_errors = True and "
                              "obs_errors is a numpy array"))

        # Test when use_errors is False
        use_errors = False
        wks_actual = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                           DataY=prob.data_pattern_out)
        cost_function_actual = 'Unweighted least squares'

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_actual, wks)
        self.assertTrue(result, msg="Failed at use_errors = False")
        self.assertEqual(cost_function_actual, cost_function,
                         msg="Failed at use_errors = False")

        # Test when use_errors is True and obs_errors is not a numpy arrray
        prob = self.NISTproblem()

        use_errors = True
        data_e = np.sqrt(prob.data_pattern_in)
        wks_actual = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                           DataY=prob.data_pattern_out,
                                           DataE=data_e)
        cost_function_actual = 'Least squares'

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks_actual, wks)
        self.assertTrue(result, msg=("Failed at use_errors = True and "
                                     "obs_errors is not a numpy array"))
        self.assertEqual(cost_function_actual, cost_function,
                         msg=("Failed at use_errors = True and "
                              "obs_errors is not a numpy array"))


    def test_get_function_definitions(self):

        # Test when prob.starting_values = None
        prob = self.NeutronProblemMock()

        function_defs_actual = [prob.equation]
        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs_actual, function_defs,
                             msg="Failed when prob.starting_values is none")

        # Test when prob.starting_values = to something
        function_defs_actual = ["name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=500.0,b2=0.0001,",
                                "name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=250.0,b2=0.0005," ]

        prob = self.NISTproblem()
        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs_actual, function_defs,
                             msg="Failed when prob.starting_values is something")


    def test_splitByString(self):

        string_actual = "..."
        name = "Irrelevant"
        min_length = 5
        loop = 4
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_actual, string)

        string_actual = "..."
        name = "TestStringRelevant"
        min_length = 5
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_actual, string)

        string_actual = "TestStringRelevant"
        name = "TestStringRelevant"
        min_length = 10
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_actual, string)

        string_actual = "TestString;\nRelevant"
        name = "TestString;Relevant"
        min_length = 5
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_actual, string)

        string_actual = "TestString;\nRelevant"
        name = "TestString;Relevant"
        min_length = 10
        loop = 2
        splitter = 3
        string = splitByString(name, min_length, loop, splitter)
        self.assertEqual(string_actual, string)


if __name__ == "__main__":
    unittest.main()
