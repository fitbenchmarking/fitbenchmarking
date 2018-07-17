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

from fitting_benchmarking import do_fitting_benchmark_group
import test_result
import test_problem


class FittingBenchmarkingGroup(unittest.TestCase):

    def basePath(self):
        ''' Helper function that returns the path to /fitbenchmarking/benchmark_problems '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')

        return bench_prob_dir


    def NISTproblemsPaths(self):

        base_path_nist = os.path.join(self.basePath(),'NIST_nonlinear_regression')
        nist_problems = ['Misra1a.dat','Lanczos3.dat','DanWood.dat']
        paths_to_nist_problems = [os.path.join(base_path_nist,nist_prob_name)
                                    for nist_prob_name in nist_problems]

        return paths_to_nist_problems


    def Misra1aProblem(self):
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


    def Lanczos3Problem(self):
        ''' Sets up the problem object for the nist problem file Lanczos3.dat '''

        data_pattern = [ [2.5134, 0.00],
                         [2.0443, 0.05],
                         [1.6684, 0.10],
                         [1.3664, 0.15],
                         [1.1232, 0.20],
                         [0.9269, 0.25],
                         [0.7679, 0.30],
                         [0.6389, 0.35],
                         [0.5338, 0.40],
                         [0.4479, 0.45],
                         [0.3776, 0.50],
                         [0.3197, 0.55],
                         [0.2720, 0.60],
                         [0.2325, 0.65],
                         [0.1997, 0.70],
                         [0.1723, 0.75],
                         [0.1493, 0.80],
                         [0.1301, 0.85],
                         [0.1138, 0.90],
                         [0.1000, 0.95],
                         [0.0883, 1.00],
                         [0.0783, 1.05],
                         [0.0698, 1.10],
                         [0.0624, 1.15] ]
        data_pattern = np.asarray(data_pattern)

        prob = test_problem.FittingTestProblem()
        prob.name = 'Lanczos3.dat'
        prob.linked_name = ("`Lanczos3.dat <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/lanczos3.dat.shtml>`__")
        prob.equation = 'b1*exp(-b2*x) + b3*exp(-b4*x) + b5*exp(-b6*x)'
        prob.starting_values = [['b1', [1.2,0.5]],
                                ['b2', [0.3,0.7]],
                                ['b3', [5.6,3.6]],
                                ['b4', [5.5,4.2]],
                                ['b5', [6.5,4]],
                                ['b6', [7.6,6.3]]]
        prob.data_pattern_in = data_pattern[:, 1:]
        prob.data_pattern_out = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 1.6117193594E-08

        return prob


    def DanWoodProblem(self):
        ''' Sets up the problem object for the nist problem file DanWood.dat '''

        data_pattern = [ [2.138, 1.309],
                         [3.421, 1.471],
                         [3.597, 1.490],
                         [4.340, 1.565],
                         [4.882, 1.611],
                         [5.660, 1.680] ]
        data_pattern = np.asarray(data_pattern)

        prob = test_problem.FittingTestProblem()
        prob.name = 'DanWood.dat'
        prob.linked_name = ("`DanWood.dat <http://www.itl.nist.gov/"
                            "div898/strd/nls/data/danwood.dat.shtml>`__")
        prob.equation = 'b1*x^b2'
        prob.starting_values = [['b1', [1,0.7]],
                                ['b2', [5,4]]]
        prob.data_pattern_in = data_pattern[:, 1:]
        prob.data_pattern_out = data_pattern[:, 0]
        prob.ref_residual_sum_sq = 4.3173084083E-03

        return prob


    def test_do_fitting_benchmark_group_nist(self):

        # Results Misra1a.dat
        prob = self.Misra1aProblem()

        MSRAresult1_actual = test_result.FittingTestResult()
        MSRAresult1_actual.problem = prob
        MSRAresult1_actual.fit_status = 'success'
        MSRAresult1_actual.fit_chi2 = 3.0142776470113924e-05
        MSRAresult1_actual.params = [234.06483564181511, 0.0005635749331078056]
        MSRAresult1_actual.errors = [486.46049489836878, 0.0013377443749239895]
        MSRAresult1_actual.sum_err_sq = 0.159784541

        MSRAresult2_actual = test_result.FittingTestResult()
        MSRAresult2_actual.problem = prob
        MSRAresult2_actual.fit_status = 'success'
        MSRAresult2_actual.fit_chi2 = 3.0142776474075721e-05
        MSRAresult2_actual.params = [234.0648164895841, 0.00056357498391696424]
        MSRAresult2_actual.errors = [486.46041069760378, 0.0013377443887498521]
        MSRAresult2_actual.sum_err_sq = 0.159784814

        # Results Lanczos3.dat
        prob = self.Lanczos3Problem()

        LANCresult1_actual = test_result.FittingTestResult()
        LANCresult1_actual.problem = prob
        LANCresult1_actual.fit_status = 'success'
        LANCresult1_actual.fit_chi2 = 1.5738994656320854e-09
        LANCresult1_actual.params = [0.076292993936269635, 0.89409819265879653,
                                     0.81196519908356291, 2.8770481720851175,
                                     1.6250509876256594, 4.959295547895354]
        LANCresult1_actual.errors = [500.12596415787573, 3219.9196370205027,
                                     1083.9772587815423, 3128.5320883517034,
                                     1574.8127529208468, 930.6176134251333]
        LANCresult1_actual.sum_err_sq = 1.54111E-08

        LANCresult2_actual = test_result.FittingTestResult()
        LANCresult2_actual.problem = prob
        LANCresult2_actual.fit_status = 'success'
        LANCresult2_actual.fit_chi2 = 1.5738994640949402e-09
        LANCresult2_actual.params = [0.076292974403935732, 0.89409808656696643,
                                     0.81196515450981444, 2.8770480616286354,
                                     1.6250510517074495, 4.9592955016636253]
        LANCresult2_actual.errors = [500.12591547373802, 3219.9201499387495,
                                     1083.9770521377736, 3128.531870980361,
                                     1574.8124979320155, 930.61746006324927]
        LANCresult2_actual.sum_err_sq = 1.54111E-08

        # Results DanWood.dat
        prob = self.DanWoodProblem()

        DANresult1_actual = test_result.FittingTestResult()
        DANresult1_actual.problem = prob
        DANresult1_actual.fit_status = 'success'
        DANresult1_actual.fit_chi2 = 0.00070750054722238179
        DANresult1_actual.params = [0.7661565792730235, 3.868179190249311]
        DANresult1_actual.errors = [0.66634945954403446, 1.905287834001421]
        DANresult1_actual.sum_err_sq = 0.004341888

        DANresult2_actual = test_result.FittingTestResult()
        DANresult2_actual.problem = prob
        DANresult2_actual.fit_status = 'success'
        DANresult2_actual.fit_chi2 = 0.00070750054796743002
        DANresult2_actual.params = [0.76615671824105447, 3.8681788388808336]
        DANresult2_actual.errors = [0.66634954507865429, 1.9052877442998983]
        DANresult2_actual.sum_err_sq = 0.004341886


        group_name = 'nist'
        problem_files = self.NISTproblemsPaths()
        minimizers = ['Levenberg-Marquardt']
        use_errors = True

        problems, results_per_problem = do_fitting_benchmark_group(group_name, problem_files,
                                                                   minimizers, use_errors)

        self.assertEqual(problems, [])

        result = results_per_problem[0][0]

        prob = result.problem
        prob_actual = MSRAresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)

        self.assertEqual(MSRAresult1_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(MSRAresult1_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(MSRAresult1_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(MSRAresult1_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(MSRAresult1_actual.params[1],result.params[1])
        self.assertAlmostEqual(MSRAresult1_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(MSRAresult1_actual.errors[1],result.errors[1])

        result = results_per_problem[1][0]

        prob = result.problem
        prob_actual = MSRAresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)

        self.assertEqual(MSRAresult2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(MSRAresult2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(MSRAresult2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(MSRAresult2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(MSRAresult2_actual.params[1],result.params[1])
        self.assertAlmostEqual(MSRAresult2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(MSRAresult2_actual.errors[1],result.errors[1])


        result = results_per_problem[2][0]

        prob = result.problem
        prob_actual = LANCresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)


        self.assertEqual(LANCresult2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(LANCresult2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(LANCresult2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(LANCresult2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(LANCresult2_actual.params[1],result.params[1], 5)
        self.assertAlmostEqual(LANCresult2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(LANCresult2_actual.errors[1],result.errors[1], 1)

        result = results_per_problem[3][0]

        prob = result.problem
        prob_actual = LANCresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)

        self.assertEqual(LANCresult2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(LANCresult2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(LANCresult2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(LANCresult2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(LANCresult2_actual.params[1],result.params[1])
        self.assertAlmostEqual(LANCresult2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(LANCresult2_actual.errors[1],result.errors[1])


        result = results_per_problem[4][0]

        prob = result.problem
        prob_actual = DANresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)

        self.assertEqual(DANresult2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(DANresult2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(DANresult2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(DANresult2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(DANresult2_actual.params[1],result.params[1], 5)
        self.assertAlmostEqual(DANresult2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(DANresult2_actual.errors[1],result.errors[1], 5)

        result = results_per_problem[5][0]

        prob = result.problem
        prob_actual = DANresult1_actual.problem
        self.assertEqual(prob.name, prob_actual.name)
        self.assertEqual(prob.linked_name, prob_actual.linked_name)
        self.assertEqual(prob.equation, prob_actual.equation)
        self.assertEqual(prob.starting_values, prob_actual.starting_values)
        self.assertEqual(prob.ref_residual_sum_sq, prob_actual.ref_residual_sum_sq)

        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_in,
                                                  prob.data_pattern_in)
        self.assertTrue(arrayTest is None)
        arrayTest = np.testing.assert_array_equal(prob_actual.data_pattern_out,
                                                  prob.data_pattern_out)
        self.assertTrue(arrayTest is None)

        self.assertEqual(DANresult2_actual.fit_status, result.fit_status)
        self.assertAlmostEqual(DANresult2_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(DANresult2_actual.sum_err_sq, result.sum_err_sq, 5)
        self.assertAlmostEqual(DANresult2_actual.params[0],result.params[0], 3)
        self.assertAlmostEqual(DANresult2_actual.params[1],result.params[1])
        self.assertAlmostEqual(DANresult2_actual.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(DANresult2_actual.errors[1],result.errors[1])


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

        wks = msapi.Load(Filename=enginxData_path)
        prob.data_pattern_in = wks.readX(0)
        prob.data_pattern_out = wks.readY(0)
        prob.data_pattern_obs_errors = wks.readE(0)
        prob.ref_residual_sum_sq = 0

        return prob


    def NeutronProblemPath(self):

        base_path_neutron = os.path.join(self.basePath(),'Neutron_data')
        neutron_problem = 'ENGINX193749_calibration_peak19.txt'
        path_to_neutron_problem = os.path.join(base_path_neutron, neutron_problem)

        return path_to_neutron_problem


    def test_do_fitting_benchmark_group_neutron(self):

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

        group_name = 'neutron'
        problem_files = [self.NeutronProblemPath()]
        minimizers = ['Levenberg-Marquardt']
        use_errors = True

        problems, results_per_problem = do_fitting_benchmark_group(group_name, problem_files,
                                                                   minimizers, use_errors)

        self.assertEqual(problems, [])

        result = results_per_problem[0][0]

        prob = result.problem
        prob_actual = result_actual.problem
        self.assertEqual(prob_actual.name, prob.name)
        self.assertEqual(prob_actual.equation, prob.equation)
        self.assertEqual(prob_actual.starting_values, prob.starting_values)
        self.assertEqual(prob_actual.start_x, prob.start_x)
        self.assertEqual(prob_actual.end_x, prob.end_x)

        self.assertEqual(result_actual.fit_status, result.fit_status)
        self.assertEqual(result_actual.fit_chi2, result.fit_chi2)
        self.assertAlmostEqual(result_actual.sum_err_sq, result.sum_err_sq)
        self.assertListEqual(result_actual.params, result.params)
        self.assertListEqual(result_actual.errors, result.errors)


    def test_do_fitting_benchmark_group_raise_error(self):

        self.assertRaises(NameError, do_fitting_benchmark_group,
                          'pasta', [self.NeutronProblemPath()],
                            ['Levenberg-Marquardt'], True)


if __name__ == "__main__":
    unittest.main()
