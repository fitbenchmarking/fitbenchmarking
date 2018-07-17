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

from results_output import build_indiv_linked_problems
from results_output import build_visual_display_page
from results_output import build_group_linked_names
from results_output import build_rst_table
from results_output import display_name_for_minimizers
from results_output import build_items_links
from results_output import calc_cell_len_rst_table
from results_output import calc_first_col_len
from results_output import build_rst_table_header_chunks
from results_output import format_cell_value_rst
from results_output import weighted_suffix_string
from post_processing import calc_accuracy_runtime_tbls
from post_processing import calc_norm_summary_tables
from post_processing import calc_summary_table


class ResultsOutput(unittest.TestCase):

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

    def GenerateResultsPerTest(self):

        # Results Misra1a.dat
        prob = self.Misra1aProblem()

        MSRAresult1 = test_result.FittingTestResult()
        MSRAresult1.problem = prob
        MSRAresult1.fit_status = 'success'
        MSRAresult1.fit_chi2 = 3.0142776470113924e-05
        MSRAresult1.params = [234.06483564181511, 0.0005635749331078056]
        MSRAresult1.errors = [486.46049489836878, 0.0013377443749239895]
        MSRAresult1.sum_err_sq = 0.159784541

        MSRAresult2 = test_result.FittingTestResult()
        MSRAresult2.problem = prob
        MSRAresult2.fit_status = 'success'
        MSRAresult2.fit_chi2 = 3.0142776474075721e-05
        MSRAresult2.params = [234.0648164895841, 0.00056357498391696424]
        MSRAresult2.errors = [486.46041069760378, 0.0013377443887498521]
        MSRAresult2.sum_err_sq = 0.159784814

        # Results Lanczos3.dat
        prob = self.Lanczos3Problem()

        LANCresult1 = test_result.FittingTestResult()
        LANCresult1.problem = prob
        LANCresult1.fit_status = 'success'
        LANCresult1.fit_chi2 = 1.5738994656320854e-09
        LANCresult1.params = [0.076292993936269635, 0.89409819265879653,
                                     0.81196519908356291, 2.8770481720851175,
                                     1.6250509876256594, 4.959295547895354]
        LANCresult1.errors = [500.12596415787573, 3219.9196370205027,
                                     1083.9772587815423, 3128.5320883517034,
                                     1574.8127529208468, 930.6176134251333]
        LANCresult1.sum_err_sq = 1.54111E-08

        LANCresult2 = test_result.FittingTestResult()
        LANCresult2.problem = prob
        LANCresult2.fit_status = 'success'
        LANCresult2.fit_chi2 = 1.5738994640949402e-09
        LANCresult2.params = [0.076292974403935732, 0.89409808656696643,
                                     0.81196515450981444, 2.8770480616286354,
                                     1.6250510517074495, 4.9592955016636253]
        LANCresult2.errors = [500.12591547373802, 3219.9201499387495,
                                     1083.9770521377736, 3128.531870980361,
                                     1574.8124979320155, 930.61746006324927]
        LANCresult2.sum_err_sq = 1.54111E-08

        # Results DanWood.dat
        prob = self.DanWoodProblem()

        DANresult1 = test_result.FittingTestResult()
        DANresult1.problem = prob
        DANresult1.fit_status = 'success'
        DANresult1.fit_chi2 = 0.00070750054722238179
        DANresult1.params = [0.7661565792730235, 3.868179190249311]
        DANresult1.errors = [0.66634945954403446, 1.905287834001421]
        DANresult1.sum_err_sq = 0.004341888

        DANresult2 = test_result.FittingTestResult()
        DANresult2.problem = prob
        DANresult2.fit_status = 'success'
        DANresult2.fit_chi2 = 0.00070750054796743002
        DANresult2.params = [0.76615671824105447, 3.8681788388808336]
        DANresult2.errors = [0.66634954507865429, 1.9052877442998983]
        DANresult2.sum_err_sq = 0.004341886

        results_per_test = [[MSRAresult1], [MSRAresult2], [LANCresult1], [LANCresult2],
                            [DANresult1], [DANresult2]]

        return results_per_test


    def test_build_indiv_linked_problems(self):



