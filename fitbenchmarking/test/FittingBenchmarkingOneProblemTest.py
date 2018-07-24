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


    def ExpectedResultObjectNeutronProblemENGINXpeak19(self):

        result = test_result.FittingTestResult()
        result.fit_status = 'success'
        result.fit_chi2 = 0.79243138659204992
        result.params = [-39.664909893833943, 0.0017093221460772121,
                                  620.29942532225425, 4.9265006277221284,
                                  0.030925377035352437, 24004.503970283724,
                                  13.856560250253684]
        result.errors = [77.066145704360949, 0.003207694697161955,
                                  109.83586635802421, 204.44335838153586,
                                  0.018928810783550146, 16.399502434549809,
                                  6.2850091287092127]
        result.sum_err_sq = 358.49892508988262

        return result


    def ExpectedResultObjectNISTproblemMisra1a(self):

        result1 = test_result.FittingTestResult()
        result1.fit_status = 'success'
        result1.fit_chi2 = 3.0142776470113924e-05
        result1.params = [234.06483564181511, 0.0005635749331078056]
        result1.errors = [486.46049489836878, 0.0013377443749239895]
        result1.sum_err_sq = 0.159784541

        result2 = test_result.FittingTestResult()
        result2.fit_status = 'success'
        result2.fit_chi2 = 3.0142776474075721e-05
        result2.params = [234.0648164895841, 0.00056357498391696424]
        result2.errors = [486.46041069760378, 0.0013377443887498521]
        result2.sum_err_sq = 0.159784814

        return result1, result2


    def ExpectedResultObjectMantidFitFails(self):

        result = test_result.FittingTestResult()
        result.fit_status = 'failed'
        result.fit_chi2 = np.nan
        result.params = np.nan
        result.errors = np.nan
        result.sum_err_sq = np.nan

        return result


    def ExpectedRunFitOutputENGINXpeak19(self):

        reference_fit_wks_path = self.NeutronProblemReferenceFitWks()
        fit_wks = msapi.Load(reference_fit_wks_path)
        status = 'success'
        chi2 = 0.79243138659204992
        params = [-39.664909893833943, 0.0017093221460772121,
                  620.29942532225425, 4.9265006277221284,
                  0.030925377035352437, 24004.503970283724,
                  13.856560250253684]
        errors = [77.066145704360949, 0.003207694697161955,
                  109.83586635802421, 204.44335838153586,
                  0.018928810783550146, 16.399502434549809,
                  6.2850091287092127]

        return status, chi2, fit_wks, params, errors


    def test_doFittingBenchmarkOneProblem_return_neutron_ENGINXpeak19_problem_result_object(self):

        prob = self.NeutronProblem()
        minimizers = ['Levenberg-Marquardt']

        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors=True,
                                                  count=0, previous_name='none')
        result_expected = self.ExpectedResultObjectNeutronProblemENGINXpeak19()
        result_expected.problem = prob

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertAlmostEqual(result_expected.fit_chi2, result.fit_chi2, 5)
        self.assertAlmostEqual(result_expected.sum_err_sq, result.sum_err_sq, 5)
        np.testing.assert_almost_equal(result_expected.params, result.params)
        np.testing.assert_almost_equal(result_expected.errors, result.errors)


    def test_doFittingBenchmarkOneProblem_return_nist_Misra1a_problem_result_object(self):

        prob = self.NISTproblem()
        minimizers = ['Levenberg-Marquardt']

        results = do_fitting_benchmark_one_problem(prob, minimizers, use_errors=True,
                                                   count=0, previous_name='none')
        result1_expected, result2_expected = self.ExpectedResultObjectNISTproblemMisra1a()
        result1_expected.problem = prob
        result2_expected.problem = prob

        result = results[0][0]
        self.assertEqual(result1_expected.problem, result.problem)
        self.assertEqual(result1_expected.fit_status, result.fit_status)
        self.assertAlmostEqual(result1_expected.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result1_expected.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result1_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(result1_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(result1_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result1_expected.errors[1],result.errors[1], 3)

        result = results[1][0]
        self.assertEqual(result2_expected.problem, result.problem)
        self.assertEqual(result2_expected.fit_status, result.fit_status)
        self.assertAlmostEqual(result2_expected.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result2_expected.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(result2_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(result2_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(result2_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(result2_expected.errors[1],result.errors[1], 3)


    def test_doFittingBenchmarkOneProblem_mantidFit_fails(self):

        prob = self.NeutronProblemMock()
        minimizers = ['Levenberg-Marquardetss']

        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors=True,
                                                  count=0, previous_name='none')
        result_expected = self.ExpectedResultObjectMantidFitFails()
        result_expected.problem = prob

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        np.testing.assert_equal(result_expected.fit_chi2, result.fit_chi2)
        np.testing.assert_equal(result_expected.sum_err_sq, result.sum_err_sq)
        np.testing.assert_equal(result_expected.params, result.params)
        np.testing.assert_equal(result_expected.errors, result.errors)


    def test_runFit_return_proper_parameters_for_neutron_problem_file_ENGINXpeak19(self):

        prob = self.NeutronProblem()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'

        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)
        (status_expected, chi2_expected, fit_wks_expected,
         params_expected, errors_expected) = self.ExpectedRunFitOutputENGINXpeak19()

        self.assertEqual(status_expected, status)
        self.assertAlmostEqual(chi2_expected, chi2, 5)
        np.testing.assert_almost_equal(params_expected, params)
        np.testing.assert_almost_equal(errors_expected, errors)
        result, messages = msapi.CompareWorkspaces(fit_wks_expected, fit_wks)
        self.assertTrue(result)


    def test_runFit_mantidFit_fails(self):

        prob = self.NeutronProblemMock()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Merquardtss'
        cost_function = 'Least squared'

        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)
        status_expected = 'failed'
        chi2_expected = np.nan
        fit_wks_expected = np.nan
        params_expected = np.nan
        errors_expected = np.nan

        self.assertEqual(status_expected, status)
        np.testing.assert_equal(chi2_expected, chi2)
        np.testing.assert_equal(params_expected, params)
        np.testing.assert_equal(errors_expected, errors)
        np.testing.assert_equal(fit_wks_expected, fit_wks)


    def test_prepareWksCostFunction_useErrors_true_and_obs_errors_np_array(self):

        prob = self.NeutronProblemMock()
        data_e = prob.data_pattern_obs_errors
        use_errors = True

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out,
                                             DataE=data_e)
        cost_function_expected = 'Least squares'

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_prepareWksCostFunction_useErrors_false(self):

        prob = self.NeutronProblemMock()
        use_errors = False

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out)
        cost_function_expected = 'Unweighted least squares'

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_prepareWksCostFunction_useErrors_true_obs_errors_not_np_array(self):

        prob = self.NISTproblem()
        data_e = np.sqrt(prob.data_pattern_in)
        use_errors = True

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                             DataY=prob.data_pattern_out,
                                             DataE=data_e)
        cost_function_expected = 'Least squares'

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_getFunctionDefinitions_starting_values_is_none(self):

        prob = self.NeutronProblemMock()

        function_defs = get_function_definitions(prob)
        function_defs_expected = [prob.equation]

        self.assertListEqual(function_defs_expected, function_defs)


    def test_getFunctionDefinitions_starting_values_is_not_none(self):

        prob = self.NISTproblem()

        function_defs = get_function_definitions(prob)
        function_defs_expected = ["name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                  "b1=500.0,b2=0.0001,",
                                  "name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                  "b1=250.0,b2=0.0005," ]

        self.assertListEqual(function_defs_expected, function_defs)


    def test_splitByString_return_dots(self):

        name = "Irrelevant"
        min_length = 5
        loop = 4
        splitter = 3

        string = splitByString(name, min_length, loop, splitter)
        string_expected = "..."

        self.assertEqual(string_expected, string)


    def test_splitByString_return_dots_after_looping(self):

        name = "TestStringRelevant"
        min_length = 5
        loop = 2
        splitter = 3

        string = splitByString(name, min_length, loop, splitter)
        string_expected = "..."

        self.assertEqual(string_expected, string)


    def test_splitByString_return_string_unmodified(self):

        name = "TestStringRelevant"
        min_length = 10
        loop = 2
        splitter = 3

        string = splitByString(name, min_length, loop, splitter)
        string_expected = "TestStringRelevant"

        self.assertEqual(string_expected, string)


    def test_splitByString_return_string_split_at_semicolon(self):

        name = "TestString;Relevant"
        min_length = 5
        loop = 2
        splitter = 3

        string = splitByString(name, min_length, loop, splitter)
        string_expected = "TestString;\nRelevant"

        self.assertEqual(string_expected, string)


    def test_splitByString_return_string_split_at_semicolon_without_calling_the_function_twice(self):

        name = "TestString;Relevant"
        min_length = 10
        loop = 2
        splitter = 3

        string = splitByString(name, min_length, loop, splitter)
        string_expected = "TestString;\nRelevant"

        self.assertEqual(string_expected, string)


if __name__ == "__main__":
    unittest.main()
