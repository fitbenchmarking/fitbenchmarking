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

    def MockProblemsDir(self):
        ''' Helper function that returns the path ../test/mock_problems/ '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        mock_problems_dir = os.path.join(current_dir, 'mock_problems')

        return mock_problems_dir


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

        # Obtained on mantid v3.12.1
        mock_problems_dir = self.MockProblemsDir()
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

        reference_fit_wks_path = self.NeutronProblemReferenceFitWks()
        prob = self.NeutronProblem()
        minimizers = ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
                      'Conjugate gradient (Polak-Ribiere imp.)',
                      'Levenberg-Marquardt', 'Levenberg-MarquardtMD',
                      'Simplex','SteepestDescent',
                      'Trust Region', 'Damped GaussNewton']
        use_errors = True
        count = 0
        previous_name = "none"
        fit_wks_actual = msapi.Load(reference_fit_wks_path)

        result_actual = test_result.FittingTestResult()
        result_actual.problem = prob
        result_actual.fit_status = 'success'
        result_actual.fit_chi2 = 0.7924313865920499
        result_actual.params = [-39.66490989383394, 0.001709322146077212, 620.2994253222543,
                                4.926500627722128, 0.030925377035352437, 24004.503970283724,
                                13.856560250253684]
        result_actual.errors = [77.06614570436095, 0.003207694697161955, 109.8358663580242,
                                204.44335838153586, 0.018928810783550146, 16.39950243454981,
                                6.285009128709213]
        result_actual.sum_err_sq = np.sum(np.square(fit_wks_actual.readY(2)))

        result = do_fitting_benchmark_one_problem(prob, minimizers, use_errors,
                                                   count, previous_name)

        self.assertEqual(result_actual.problem, result[0].problem)
        self.assertEqual(result_actual.fit_status, result[0].fit_status)
        self.assertEqual(result_actual.fit_chi2, result[0].fit_chi2)
        self.assertEqual(result_actual.sum_err_sq, result[0].sum_err_sq)
        self.assertListEqual(result_actual.params, result[0].params)
        self.assertListEqual(result_actual.errors, result[0].errors)


    def test_run_fit(self):

        reference_fit_wks_path = self.NeutronProblemReferenceFitWks()
        status_actual = 'success'
        chi2_actual = 0.7924313865920499
        fit_wks_actual = msapi.Load(reference_fit_wks_path)
        params_actual = [-39.66490989383394, 0.001709322146077212, 620.2994253222543,
                         4.926500627722128, 0.030925377035352437, 24004.503970283724,
                         13.856560250253684]
        errors_actual = [77.06614570436095, 0.003207694697161955, 109.8358663580242,
                         204.44335838153586, 0.018928810783550146, 16.39950243454981,
                         6.285009128709213]

        prob = self.NeutronProblem()
        wks = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                    DataY=prob.data_pattern_out,
                                    DataE=prob.data_pattern_obs_errors)
        function = prob.equation
        minimizer = 'Levenberg-Marquardt'
        cost_function = 'Least squares'
        status, chi2, fit_wks, params, errors = run_fit(wks, prob, function,
                                                        minimizer, cost_function)

        self.assertEqual(status,status_actual)
        self.assertEqual(chi2,chi2_actual)
        self.assertListEqual(params,params_actual)
        self.assertListEqual(errors,errors_actual)
        result, messages = msapi.CompareWorkspaces(fit_wks, fit_wks_actual)
        self.assertTrue(result)


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

        result, messages = msapi.CompareWorkspaces(wks, wks_actual)
        self.assertTrue(result, msg=("Failed at use_errors = True and "
                                     "obs_errors is a numpy array"))
        self.assertEqual(cost_function, cost_function_actual,
                         msg=("Failed at use_errors = True and "
                              "obs_errors is a numpy array"))

        # Test when use_errors is False
        use_errors = False
        wks_actual = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                           DataY=prob.data_pattern_out)
        cost_function_actual = 'Unweighted least squares'

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks, wks_actual)
        self.assertTrue(result, msg="Failed at use_errors = False")
        self.assertEqual(cost_function, cost_function_actual,
                         msg="Failed at use_errors = False")

        # Test when use_errors is True and obs_errors is not a numpy arrray
        use_errors = True
        prob.data_pattern_obs_errors = 0
        data_e = np.sqrt(prob.data_pattern_in)
        wks_actual = msapi.CreateWorkspace(DataX=prob.data_pattern_in,
                                           DataY=prob.data_pattern_out,
                                           DataE=data_e)
        cost_function_actual = 'Least Squares'

        wks, cost_function = prepare_wks_cost_function(prob, use_errors)

        result, messages = msapi.CompareWorkspaces(wks, wks_actual)
        self.assertTrue(result, msg=("Failed at use_errors = True and "
                                     "obs_errors is not a numpy array"))
        self.assertEqual(cost_function, cost_function_actual,
                         msg=("Failed at use_errors = True and "
                              "obs_errors is not a numpy array"))


    def test_get_function_definitions(self):

        prob = self.NeutronProblemMock()
        function_defs_actual = [prob.equation]

        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs, function_defs_actual,
                             msg="Failed when prob.starting_values is none")

        prob = self.NISTproblem()
        function_defs_actual = ["name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=500.0,b2=0.0001,",
                                "name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=250.0,b2=0.0005," ]

        function_defs = get_function_definitions(prob)

        self.assertListEqual(function_defs, function_defs_actual,
                             msg="Failed when prob.starting_values is something")


if __name__ == "__main__":
    unittest.main()
