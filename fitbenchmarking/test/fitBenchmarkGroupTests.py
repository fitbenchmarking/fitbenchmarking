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

from fitting_benchmarking import do_fitting_benchmark_group
import test_result
import test_problem


class FittingBenchmarkingGroup(unittest.TestCase):

    def DumpDir(self):
        """
        Path to a directory where file output of various functions
        is dumped.
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        dump_dir = os.path.join(current_dir, 'dump')

        return dump_dir

    def basePath(self):
        '''
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')

        return bench_prob_dir


    def NISTproblemsPaths(self):
        ''' Helper function that returns the paths to three nist problems '''

        base_path_nist = os.path.join(self.basePath(),
                                      'NIST_nonlinear_regression')
        paths_to_nist_problems = [os.path.join(base_path_nist, 'Misra1a.dat')]

        return paths_to_nist_problems


    def Misra1aProblem(self):
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


    def ExpectedResultsMisra1aProblem(self):

        prob = self.Misra1aProblem()

        result1 = test_result.FittingTestResult()
        result1.problem = prob
        result1.fit_status = 'success'
        result1.chi_sq = 0.153327121
        result1.params = [234.53440075754128, 0.00056228017032756289]
        result1.errors = [166.95843730560517, 0.00045840028643556361]
        result1.minimizer = 'Levenberg-Marquardt'
        result1.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=500.0,b2=0.0001,")

        result2 = test_result.FittingTestResult()
        result2.problem = prob
        result2.fit_status = 'success'
        result2.chi_sq = 0.153326918
        result2.params = [234.53441741161569, 0.00056228012624728884]
        result2.errors = [166.95846246387609, 0.00045840028235511008]
        result2.minimizer = 'Levenberg-Marquardt'
        result2.function_def = ("name=UserFunction, Formula=b1*(1-exp(-b2*x)), "
                                "b1=250.0,b2=0.0005,")

        return result1, result2


    def EnginxDataPath(self):
        ''' Helper function that returns the path to the Enginx data
            i.e. benchmark_problems/Neutron_data/data_files/
            ENGINX193749_calibration_spec651.nxs '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        enginxData_path = os.path.join(bench_prob_dir, 'Neutron_data',
                                       'data_files',
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
        prob.data_x = wks.readX(0)
        prob.data_y = wks.readY(0)
        prob.data_pattern_obs_errors = wks.readE(0)
        prob.ref_residual_sum_sq = 0

        return prob


    def NeutronProblemPath(self):
        ''' Helper function that returns the path to the neutron problem
            ENGINX193749_calibration_peak19.txt '''

        base_path_neutron = os.path.join(self.basePath(),'Neutron_data')
        neutron_problem = 'ENGINX193749_calibration_peak19.txt'
        path_to_neutron_problem = os.path.join(base_path_neutron, neutron_problem)

        return path_to_neutron_problem


    def ExpectedResultsENGINXpeak19(self):

        prob = self.NeutronProblem()

        result = test_result.FittingTestResult()
        result.problem = prob
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


    def test_doFittingBenchmarkGroup_return_results_for_NIST_problems_Misra1a_Lanczos3_and_DanWood(self):

        dump_dir = self.DumpDir()
        group_name = 'nist'
        problem_files = self.NISTproblemsPaths()
        minimizers = ['Levenberg-Marquardt']
        use_errors = True

        results_per_problem = \
        do_fitting_benchmark_group(group_name, dump_dir, problem_files,
                                   minimizers, use_errors)
        MSRAres1_expected, MSRAres2_expected = \
        self.ExpectedResultsMisra1aProblem()

        result = results_per_problem[0][0]
        prob = result.problem
        prob_expected = MSRAres1_expected.problem
        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.linked_name, prob.linked_name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.ref_residual_sum_sq, prob.ref_residual_sum_sq)
        np.testing.assert_array_equal(prob_expected.data_x, prob.data_x)
        np.testing.assert_array_equal(prob_expected.data_y, prob.data_y)

        self.assertEqual(MSRAres1_expected.fit_status, result.fit_status)
        self.assertEqual(MSRAres1_expected.minimizer, result.minimizer)
        self.assertEqual(MSRAres1_expected.function_def, result.function_def)
        self.assertAlmostEqual(MSRAres1_expected.chi_sq, result.chi_sq, 5)
        self.assertAlmostEqual(MSRAres1_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(MSRAres1_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(MSRAres1_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(MSRAres1_expected.errors[1],result.errors[1], 3)


        result = results_per_problem[1][0]
        prob = result.problem
        prob_expected = MSRAres2_expected.problem
        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.linked_name, prob.linked_name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.ref_residual_sum_sq, prob.ref_residual_sum_sq)
        np.testing.assert_array_equal(prob_expected.data_x, prob.data_x)
        np.testing.assert_array_equal(prob_expected.data_y, prob.data_y)

        self.assertEqual(MSRAres2_expected.fit_status, result.fit_status)
        self.assertEqual(MSRAres2_expected.minimizer, result.minimizer)
        self.assertEqual(MSRAres2_expected.function_def, result.function_def)
        self.assertAlmostEqual(MSRAres2_expected.chi_sq, result.chi_sq, 5)
        self.assertAlmostEqual(MSRAres2_expected.params[0],result.params[0], 3)
        self.assertAlmostEqual(MSRAres2_expected.params[1],result.params[1], 3)
        self.assertAlmostEqual(MSRAres2_expected.errors[0],result.errors[0], 3)
        self.assertAlmostEqual(MSRAres2_expected.errors[1],result.errors[1], 3)


    def test_doFittingBenchmarkGroup_neutron_return_results_ENGINXpeak19_problem(self):

        dump_dir = self.DumpDir()
        group_name = 'neutron'
        problem_files = [self.NeutronProblemPath()]
        minimizers = ['Levenberg-Marquardt']
        use_errors = True

        results_per_problem = \
        do_fitting_benchmark_group(group_name, dump_dir, problem_files,
                                   minimizers, use_errors)
        result_expected = self.ExpectedResultsENGINXpeak19()

        result = results_per_problem[0][0]
        prob = result.problem
        prob_expected = result_expected.problem
        self.assertEqual(prob_expected.name, prob.name)
        self.assertEqual(prob_expected.equation, prob.equation)
        self.assertEqual(prob_expected.starting_values, prob.starting_values)
        self.assertEqual(prob_expected.start_x, prob.start_x)
        self.assertEqual(prob_expected.end_x, prob.end_x)

        self.assertEqual(result_expected.fit_status, result.fit_status)
        self.assertEqual(result_expected.minimizer, result.minimizer)
        self.assertEqual(result_expected.function_def, result.function_def)
        self.assertAlmostEqual(result_expected.chi_sq, result.chi_sq, 5)
        np.testing.assert_almost_equal(result_expected.params, result.params)
        np.testing.assert_almost_equal(result_expected.errors, result.errors)


    def test_doFittingBenchmarkGroup_raise_error_invalid_group_name(self):

        dump_dir = self.DumpDir()
        self.assertRaises(NameError, do_fitting_benchmark_group, 'pasta',
                          dump_dir, [self.NeutronProblemPath()],
                          ['Levenberg-Marquardt'], True)


if __name__ == "__main__":
    unittest.main()
