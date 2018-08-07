from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from fitting_benchmarking import get_nist_problem_files
from fitting_benchmarking import get_neutron_problem_files
# from fitting_benchmarking import get_muon_problem_files
# from fitting_benchmarking import get_cutest_problem_files


class GetProblemFilesTest(unittest.TestCase):

    def basePath(self):
        ''' Helper function that returns the path to /fitbenchmarking/benchmark_problems '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.sep.join(current_dir.split(os.path.sep)[:-2])
        bench_prob_dir = os.path.join(base_dir, 'benchmark_problems')
        return bench_prob_dir


    def neutronProblems(self):

        neutron_problems = [['ENGINX193749_calibration_peak19.txt',
                             'ENGINX193749_calibration_peak20.txt',
                             'ENGINX193749_calibration_peak23.txt',
                             'ENGINX193749_calibration_peak5.txt',
                             'ENGINX193749_calibration_peak6.txt',
                             'ENGINX236516_vanadium_bank1_10brk.txt',
                             'ENGINX236516_vanadium_bank1_20brk.txt',
                             'EVS14188-90_Gaussian_peaks_1.txt',
                             'EVS14188-90_Gaussian_peaks_2.txt',
                             'GEMpeak1.txt',
                             'WISH17701_peak1.txt', 'WISH17701_peak2.txt',
                             'WISH17701_peak3.txt', 'WISH17701_peak4.txt',
                             'WISH17701_peak5.txt', 'WISH17701_peak6.txt',
                             'WISH17701_peak7.txt', 'WISH17701_peak8.txt',
                             'WISH17701_peak9.txt']]

        return neutron_problems


    def test_getNISTproblemFiles_return_expected_paths(self):

        base_path_nist = os.path.join(self.basePath(),'NIST_nonlinear_regression')
        nist_problems = [['Misra1a.dat', 'Chwirut2.dat', 'Chwirut1.dat',
                          'Lanczos3.dat', 'Gauss1.dat', 'Gauss2.dat',
                          'DanWood.dat', 'Misra1b.dat'],
                         ['Kirby2.dat', 'Hahn1.dat','MGH17.dat',
                          'Lanczos1.dat', 'Lanczos2.dat','Gauss3.dat',
                          'Misra1c.dat', 'Misra1d.dat','ENSO.dat'],
                         ['MGH09.dat', 'Thurber.dat', 'BoxBOD.dat', 'Rat42.dat',
                          'MGH10.dat', 'Eckerle4.dat', 'Rat43.dat', 'Bennett5.dat']]

        paths_to_nist_problems = get_nist_problem_files(base_path_nist)
        # This for loop (and similar ones in other tests)
        # attaches the proper path to a problem file name
        # e.g. Misra1a.dat becomes
        # d:/fitbenchmarking/benchmark_problems/NIST_nonlinear_regression/Misra1a.dat
        paths_to_nist_problems_expected = []
        for nist_level_group in nist_problems:
            paths_to_level_group = [os.path.join(base_path_nist,nist_prob_name)
                                    for nist_prob_name in nist_level_group]
            paths_to_nist_problems_expected.append(paths_to_level_group)

        self.assertListEqual(paths_to_nist_problems_expected,
                             paths_to_nist_problems)


    def test_getNeutronProblemFiles_return_expected_neutron_paths(self):

        base_path_neutron = os.path.join(self.basePath(),'Neutron_data')
        neutron_problems = self.neutronProblems()

        paths_to_neutron_problems = \
        get_neutron_problem_files(base_path_neutron)[0]
        # Please see the above for loop comments for a description of this one
        paths_to_neutron_problems_expected = []
        for neutron_level_group in neutron_problems:
            paths_to_level_group = \
            [os.path.join(base_path_neutron,neutron_prob_name)
             for neutron_prob_name in neutron_level_group]
            paths_to_neutron_problems_expected.append(paths_to_level_group)

        self.assertListEqual(paths_to_neutron_problems_expected[0],
                             paths_to_neutron_problems)


if __name__ == "__main__":
    unittest.main()
