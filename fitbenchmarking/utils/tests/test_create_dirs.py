from __future__ import (absolute_import, division, print_function)

import unittest
import os
import shutil

from fitbenchmarking.utils.create_dirs import figures
from fitbenchmarking.utils.create_dirs import group_results
from fitbenchmarking.utils.create_dirs import results


class CreateDirsTests(unittest.TestCase):

    def setUp(self):
        self.results_dir = os.path.join(os.getcwd(), 'results')

    def test_results_throw_correct_error(self):

        self.assertRaises(TypeError, results, 123)
        self.assertRaises(TypeError, results, None)

    def test_results_create_correct_dir(self):

        results_dir = os.path.join(os.getcwd(), "full_path", "test")
        results_dir = results(results_dir)
        results_dir_expected = os.path.join(os.getcwd(), "full_path", "test")

        self.assertEqual(results_dir_expected, results_dir)

        shutil.rmtree(results_dir_expected)
        os.rmdir(os.path.join(os.getcwd(), "full_path"))

    def test_groupResults_create_correct_group_results(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")
        group_results_dir_expected = os.path.join(results_dir, "test_group")

        self.assertEqual(group_results_dir_expected, group_results_dir)
        self.assertTrue(os.path.exists(group_results_dir_expected))

        shutil.rmtree(results_dir)

    def test_figures_create_correct_dir(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")

        figures_dir = figures(group_results_dir)
        figures_dir_expected = os.path.join(group_results_dir, 'support_pages',
                                            'figures')

        self.assertEqual(figures_dir_expected, figures_dir)
        self.assertTrue(os.path.exists(figures_dir_expected))

        shutil.rmtree(results_dir)


if __name__ == "__main__":
    unittest.main()
