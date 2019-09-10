from __future__ import (absolute_import, division, print_function)

import unittest
import os
import shutil
import json

# Delete four lines below when automated tests are enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)
sys.path.insert(0, parent_dir)

from misc import get_minimizers
from misc import setup_fitting_problems
from misc import get_problem_files


class CreateDirsTests(unittest.TestCase):

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

  def all_nist_problems(self):
    """
    Helper function that returns the names of Nist low diff problems.
    """

    nist_ld_problems = [['Misra1a.dat', 'Chwirut2.dat', 'Chwirut1.dat',
                         'Lanczos3.dat', 'Gauss1.dat', 'Gauss2.dat',
                         'DanWood.dat', 'Misra1b.dat']]

    return nist_ld_problems

  def get_minimizers_file(self):

    current_path = os.path.dirname(os.path.realpath(__file__))
    utils_path = os.path.abspath(os.path.join(current_path, os.pardir))
    fitbm_path = os.path.abspath(os.path.join(utils_path, os.pardir))
    minimizer_json = os.path.join(fitbm_path,
                                  "fitbenchmarking_default_options.json")
    return str(minimizer_json)

  def test_getMinimizers_load_correct_minimizers_mantid_default(self):

    software_options = {'software': 'mantid', 'minimizer_options': None}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = \
        ["BFGS", "Conjugate gradient (Fletcher-Reeves imp.)",
         "Conjugate gradient (Polak-Ribiere imp.)", "Damped GaussNewton",
         "Levenberg-Marquardt", "Levenberg-MarquardtMD", "Simplex",
         "SteepestDescent", "Trust Region"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_minimizers_scipy_default(self):

    software_options = {'software': 'scipy', 'minimizer_options': None}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = ["lm", "trf", "dogbox"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_minimizers_scipy_min_list(self):

    software_options = {'software': 'scipy',
                        'minimizer_options': {"scipy": ["lm", "trf"]}}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = ["lm", "trf"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_minimizers_mantid_min_list(self):

    software_options = {'software': 'mantid',
                        'minimizer_options': {"mantid": ["BFGS", "Conjugate gradient (Fletcher-Reeves imp.)", "Conjugate gradient (Polak-Ribiere imp.)"]}}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = ["BFGS", "Conjugate gradient (Fletcher-Reeves imp.)", "Conjugate gradient (Polak-Ribiere imp.)"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_minimizers_scipy_read_file(self):
    software_options = {'software': 'scipy',
                        'minimizer_options': None,
                        'options_file': self.get_minimizers_file()}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = ["lm", "trf", "dogbox"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_minimizers_mantid_read_file(self):

    software_options = {'software': 'mantid',
                        'minimizer_options': None,
                        'options_file': self.get_minimizers_file()}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = ["BFGS", "Conjugate gradient (Fletcher-Reeves imp.)",
                          "Conjugate gradient (Polak-Ribiere imp.)",
                          "Damped GaussNewton",
                          "Levenberg-Marquardt", "Levenberg-MarquardtMD",
                          "Simplex", "SteepestDescent",
                          "Trust Region"]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_load_correct_compare_minimizers_mantid_read_file(self):

    software_options = {'software': ['mantid', 'scipy'],
                        'minimizer_options': None,
                        'options_file': self.get_minimizers_file()}

    minimizers, _ = get_minimizers(software_options)
    minmizers_expected = [["BFGS", "Conjugate gradient (Fletcher-Reeves imp.)",
                           "Conjugate gradient (Polak-Ribiere imp.)",
                           "Damped GaussNewton",
                           "Levenberg-Marquardt", "Levenberg-MarquardtMD",
                           "Simplex", "SteepestDescent",
                           "Trust Region"],
                          ["lm", "trf", "dogbox"]]

    self.assertListEqual(minmizers_expected, minimizers)

  def test_getMinimizers_value_error_incorrect_input_software_options(self):

    software_options = 2

    self.assertRaises(ValueError, get_minimizers, software_options)

  def test_getMinimizers_value_error_incorrect_input_minimizer_options(self):

    software_options = {'software': 'mantid',
                        'minimizer_options': 1}

    self.assertRaises(ValueError, get_minimizers, software_options)

  def test_setupFittingProblems_get_correct_nist_probs(self):

    data_dir = os.path.join(self.base_path(), 'NIST', 'low_difficulty')
    nist_problems = self.all_nist_problems()

    problem_groups = setup_fitting_problems(data_dir, 'NIST_low_diff')
    problem_groups_expected = {'NIST_low_diff': nist_problems}

    self.assertTrue(problem_groups_expected, problem_groups)

  def test_setupFittingProblems_get_correct_neutron_probs(self):

    data_dir = os.path.join(self.base_path(), 'Neutron')
    neutron_problems = self.all_neutron_problems()

    problem_groups = setup_fitting_problems(data_dir, 'Neutron')
    problem_groups_expected = {'nist': neutron_problems}

    self.assertTrue(problem_groups_expected, problem_groups)

  def test_getProblemFiles_return_expected_neutron_paths(self):

    base_path_neutron = os.path.join(self.base_path(), 'Neutron')
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
