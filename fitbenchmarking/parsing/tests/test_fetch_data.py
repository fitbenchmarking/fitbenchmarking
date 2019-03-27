from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests are enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from parsing.fetch_data import get_problem_files


class FetchDataTests(unittest.TestCase):

    def base_path(self):
        """
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(os.path.normpath(test_dir))
        main_dir = os.path.dirname(os.path.normpath(parent_dir))
        root_dir = os.path.dirname(os.path.normpath(main_dir))
        bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')

        return bench_prob_dir

    def all_neutron_problems(self):
        """
        Helper function that returns the names of all neutron problems.
        """

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

    def test_getProblemFiles_return_expected_neutron_paths(self):

        base_path_neutron = os.path.join(self.base_path(), 'Neutron_data')
        neutron_problems = self.all_neutron_problems()

        paths_to_neutron_problems = \
            get_problem_files(base_path_neutron)[0]
        # Please see the above for loop comments for
        # a description of this one
        paths_to_neutron_problems_expected = []
        for neutron_level_group in neutron_problems:
            paths_to_level_group = \
                [os.path.join(base_path_neutron, neutron_prob_name)
                 for neutron_prob_name in neutron_level_group]
            paths_to_neutron_problems_expected.append(paths_to_level_group)

        self.assertListEqual(paths_to_neutron_problems_expected[0],
                             paths_to_neutron_problems)


if __name__ == "__main__":
    unittest.main()
