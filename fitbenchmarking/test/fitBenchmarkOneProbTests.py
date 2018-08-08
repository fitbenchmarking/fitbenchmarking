from __future__ import (absolute_import, division, print_function)

import unittest
import os
import mantid.simpleapi as msapi
import numpy as np

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from fitting_benchmarking import do_fitting_benchmark_one_problem
from fitting_benchmarking import calculate_chi_sq
from fitting_benchmarking import prepare_wks_cost_function
from fitting_benchmarking import get_function_definitions
from fitting_benchmarking import run_fit
import test_result
import test_problem


class FittingBenchmarkingOneProblem(unittest.TestCase):

    def DumpDir(self):
        """
        Path to a directory where file output of various functions
        is dumped.
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        dump_dir = os.path.join(current_dir, 'dump')

        return dump_dir


    def MockFitWksPath(self):

        current_dir = os.path.dirname(os.path.realpath(__file__))
        mock_fitwks = os.path.join(current_dir, 'mock_problems', 'data_files',
                                   'fitWorkspace_enginxPeak19')

        return mock_fitwks


    def EnginxDataPath(self):
        """ Helper function that returns the path ../benchmark_problems/ """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        enginxData_path = os.path.join(bench_prob_dir, 'Neutron_data',
                                       'data_files',
                                       'ENGINX193749_calibration_spec651.nxs')

        return enginxData_path


    def NeutronProblem(self):
        """
        Sets up the problem object for the neutron problem file:
        ENGINX193749_calibration_peak19.txt
        """

        enginxData_path = self.EnginxDataPath()

        prob = test_problem.FittingTestProblem()
        prob.name = 'ENGINX 193749 calibration, spectrum 651, peak 19'
        prob.equation = ("name=LinearBackground;"
                         "name=BackToBackExponential,"
                         "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")
        prob.starting_values = None
        prob.start_x = 23919.5789114
        prob.end_x = 24189.3183142

        wks = msapi.Load(Filename=enginxData_path)
        prob.data_x = wks.readX(0)
        prob.data_y = wks.readY(0)
        prob.data_pattern_obs_errors = wks.readE(0)
        prob.ref_residual_sum_sq = 0

        return prob


    def NeutronProblemMock(self):
        """
        Sets up the problem object for the neutron problem file:
        ENGINX193749_calibration_peak19.txt with mock data entires
        """

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
        prob.data_x = np.arange(10)
        prob.data_y = 100*np.arange(9)
        prob.data_pattern_obs_errors = np.sqrt(prob.data_y)
        prob.ref_residual_sum_sq = 0

        return prob


    def NISTproblem(self):
        """ Sets up the problem object for the nist problem file Misra1a.dat """

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
        prob.name = 'Misra1a'
        prob.linked_name = ("`Misra1a <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/misra1a.shtml>`__")
        prob.equation = 'b1*(1-exp(-b2*x))'
        prob.starting_values = [['b1', [500.0,250.0]],
                                ['b2', [0.0001,0.0005]]]
        prob.data_x = data_pattern[:, 1]
        prob.data_y = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.2455138894E-01

        return prob


    def ExpectedResultObjectNeutronProblemENGINXpeak19(self):

        result = test_result.FittingTestResult()
        result.fit_status = 'success'
        result.chi_sq = 358.49892508988262
        result.params = [-39.664909893833943, 0.0017093221460772121,
                         620.29942532225425, 4.9265006277221284,
                         0.030925377035352437, 24004.503970283724,
                         13.856560250253684]
        result.errors = [77.066145704360949, 0.003207694697161955,
                         109.83586635802421, 204.44335838153586,
                         0.018928810783550146, 16.399502434549809,
                         6.2850091287092127]
        result.minimizer = 'Levenberg-Marquardt'
        result.function_def = ("name=LinearBackground;"
                               "name=BackToBackExponential,"
                               "I=597.076,A=1,B=0.05,X0=24027.5,S=22.9096")

        return result


    def ExpectedResultObjectNISTproblemMisra1a(self):

        result1 = test_result.FittingTestResult()
        result1.fit_status = 'success'
        result1.chi_sq = 0.153327121
        result1.params = [234.53440075754128, 0.00056228017032756289]
        result1.errors = [166.95843730560517, 0.00045840028643556361]
        result1.minimizer = 'Levenberg-Marquardt'
        result1.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=500.0,b2=0.0001,")

        result2 = test_result.FittingTestResult()
        result2.fit_status = 'success'
        result2.chi_sq = 0.153326918
        result2.params = [234.53441741161569, 0.00056228012624728884]
        result2.errors = [166.95846246387609, 0.00045840028235511008]
        result2.minimizer = 'Levenberg-Marquardt'
        result2.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=250.0,b2=0.0005,")

        return result1, result2


    def ExpectedResultObjectMantidFitFails(self):
        """ Expected result object for when the fit fails """

        result = test_result.FittingTestResult()
        result.fit_status = 'failed'
        result.chi_sq = np.nan
        result.params = None
        result.errors = None

        return result


    def test_doFittingBenchmarkOneProblem_return_neutron_ENGINXpeak19_problem_result_object(self):

        dump_dir = self.DumpDir()
        prob = self.NeutronProblem()
        minimizers = ['Levenberg-Marquardt']

        result = do_fitting_benchmark_one_problem(prob, dump_dir, minimizers,
                                                  use_errors=True, count=0)
        result_expected = self.ExpectedResultObjectNeutronProblemENGINXpeak19()
        result_expected.problem = prob

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertEqual(result_expected.minimizer, result.minimizer)
        self.assertEqual(result_expected.function_def, result.function_def)
        self.assertAlmostEqual(result_expected.chi_sq, result.chi_sq, 1)
        np.testing.assert_almost_equal(result_expected.params, result.params)
        np.testing.assert_almost_equal(result_expected.errors, result.errors)


    def test_doFittingBenchmarkOneProblem_return_nist_Misra1a_problem_result_object(self):

        dump_dir = self.DumpDir()
        prob = self.NISTproblem()
        minimizers = ['Levenberg-Marquardt']

        print(dump_dir)
        results = do_fitting_benchmark_one_problem(prob, dump_dir, minimizers,
                                                   use_errors=True, count=0)
        res1_expected, res2_expected = \
        self.ExpectedResultObjectNISTproblemMisra1a()
        res1_expected.problem = prob
        res2_expected.problem = prob


        result = results[0][0]
        self.assertEqual(res1_expected.problem, result.problem)
        self.assertEqual(res1_expected.fit_status, result.fit_status)
        self.assertEqual(res1_expected.minimizer, result.minimizer)
        self.assertEqual(res1_expected.function_def, result.function_def)
        self.assertAlmostEqual(res1_expected.chi_sq, result.chi_sq, 5)
        self.assertAlmostEqual(res1_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(res1_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(res1_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(res1_expected.errors[1],result.errors[1], 3)

        result = results[1][0]
        self.assertEqual(res2_expected.problem, result.problem)
        self.assertEqual(res2_expected.fit_status, result.fit_status)
        self.assertEqual(res2_expected.minimizer, result.minimizer)
        self.assertEqual(res2_expected.function_def, result.function_def)
        self.assertAlmostEqual(res2_expected.chi_sq, result.chi_sq, 5)
        self.assertAlmostEqual(res2_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(res2_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(res2_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(res2_expected.errors[1],result.errors[1], 3)


    def test_doFittingBenchmarkOneProblem_mantidFit_fails(self):

        dump_dir = self.DumpDir()
        prob = self.NeutronProblemMock()
        minimizers = ['Levenberg-Marquardetss']

        result = do_fitting_benchmark_one_problem(prob, dump_dir, minimizers,
                                                  use_errors=True, count=0)
        result_expected = self.ExpectedResultObjectMantidFitFails()
        result_expected.problem = prob

        result = result[0][0]
        self.assertEqual(result_expected.problem, result.problem)
        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertEqual(result_expected.params, result.params)
        self.assertEqual(result_expected.errors, result.errors)
        np.testing.assert_equal(result_expected.chi_sq, result.chi_sq)


    def test_calculateChiSquared_return_minChisq_proper(self):

        fit_wks_path = self.MockFitWksPath()
        fit_wks = msapi.Load(fit_wks_path)
        min_chi_sq = 400
        best_fit = None
        minimizer_name = 'Levenberg-Marquardt'

        chi_sq, min_chi_sq, best_fit = \
        calculate_chi_sq(fit_wks, min_chi_sq, best_fit, minimizer_name)
        chi_sq_expected = 358.49892508988262
        min_chi_sq_expected = 358.49892508988262

        self.assertAlmostEqual(chi_sq_expected, chi_sq, 5)
        self.assertAlmostEqual(min_chi_sq_expected, min_chi_sq, 5)


    def test_calculateChiSquared_return_minChisq_not_changed(self):

        fit_wks_path = self.MockFitWksPath()
        fit_wks = msapi.Load(fit_wks_path)
        min_chi_sq = 300
        best_fit = None
        minimizer_name = 'Levenberg-Marquardt'

        chi_sq, min_chi_sq, best_fit = \
        calculate_chi_sq(fit_wks, min_chi_sq, best_fit, minimizer_name)
        chi_sq_expected = 358.49892508988262
        min_chi_sq_expected = 300

        self.assertAlmostEqual(chi_sq_expected, chi_sq, 5)
        self.assertAlmostEqual(min_chi_sq_expected, min_chi_sq, 5)


    def test_calculateChiSquared_return_nan(self):

        fit_wks = None
        min_chi_sq = 300
        best_fit = None
        minimizer_name = 'Levenberg-Marquardt'

        chi_sq, min_chi_sq, best_fit = \
        calculate_chi_sq(fit_wks, min_chi_sq, best_fit, minimizer_name)
        chi_sq_expected = np.nan
        min_chi_sq_expected = 300

        np.testing.assert_equal(chi_sq_expected, chi_sq)
        self.assertAlmostEqual(min_chi_sq_expected, min_chi_sq, 5)


    def test_runFit_return_proper_parameters_for_neutron_problem_file_ENGINXpeak19(self):

        prob = self.NeutronProblem()
        wks = msapi.CreateWorkspace(DataX=prob.data_x,
                                    DataY=prob.data_y,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'

        status, fit_wks, params, errors = \
        run_fit(wks, prob, function, minimizer, cost_function)
        results_expected = self.ExpectedResultObjectNeutronProblemENGINXpeak19()
        status_expected = results_expected.fit_status
        params_expected = results_expected.params
        errors_expected = results_expected.errors

        self.assertEqual(status_expected, status)
        np.testing.assert_almost_equal(params_expected, params, 1)
        np.testing.assert_almost_equal(errors_expected, errors, 1)


    def test_runFit_mantidFit_fails(self):

        prob = self.NeutronProblemMock()
        wks = msapi.CreateWorkspace(DataX=prob.data_x,
                                    DataY=prob.data_y,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Merquardtss'
        cost_function = 'Least squared'

        status, fit_wks, params, errors = \
        run_fit(wks, prob, function, minimizer, cost_function)
        status_expected = 'failed'
        fit_wks_expected = None
        params_expected = None
        errors_expected = None

        self.assertEqual(status_expected, status)
        np.testing.assert_equal(fit_wks_expected, fit_wks)
        np.testing.assert_equal(params_expected, params)
        np.testing.assert_equal(errors_expected, errors)


    def test_prepareWksCostFunction_useErrors_true_and_obs_errors_np_array(self):

        prob = self.NeutronProblemMock()
        data_e = prob.data_pattern_obs_errors
        use_errors = True

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_x,
                                             DataY=prob.data_y,
                                             DataE=data_e)
        cost_function_expected = 'Least squares'

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_prepareWksCostFunction_useErrors_false(self):

        prob = self.NeutronProblemMock()
        use_errors = False

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_x,
                                             DataY=prob.data_y)
        cost_function_expected = 'Unweighted least squares'

        result, messages = msapi.CompareWorkspaces(wks_expected, wks)
        self.assertTrue(result)
        self.assertEqual(cost_function_expected, cost_function)


    def test_prepareWksCostFunction_useErrors_true_obs_errors_not_np_array(self):

        prob = self.NISTproblem()
        data_e = np.sqrt(prob.data_y)
        use_errors = True

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)
        wks_expected = msapi.CreateWorkspace(DataX=prob.data_x,
                                             DataY=prob.data_y,
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
        function_defs_expected = ["name=UserFunction, "
                                  "Formula=b1*(1-exp(-b2*x)), "
                                  "b1=500.0,b2=0.0001,",
                                  "name=UserFunction, "
                                  "Formula=b1*(1-exp(-b2*x)), "
                                  "b1=250.0,b2=0.0005," ]

        self.assertListEqual(function_defs_expected, function_defs)


if __name__ == "__main__":
    unittest.main()
