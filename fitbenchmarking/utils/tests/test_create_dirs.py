from __future__ import (absolute_import, division, print_function)

import unittest
import os
import shutil

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
sys.path.insert(0, parent_dir)

from create_dirs import results
from create_dirs import group_results
from create_dirs import restables_dir
from create_dirs import figures


class CreateDirsTests(unittest.TestCase):

    def test_results_create_correct_None_dir(self):

        results_dir = None
        results_dir = results(results_dir)
        results_dir_expected = os.path.join(os.getcwd(), "results")

        self.assertEqual(results_dir_expected, results_dir)

        shutil.rmtree(results_dir_expected)

    def test_results_throw_correct_error(self):

        results_dir = 123

        self.assertRaises(TypeError, results, results_dir)

    def test_results_create_correct_custom_dir(self):

        results_dir = "TestResult"
        results_dir = results(results_dir)
        results_dir_expected = os.path.join(os.getcwd(), "TestResult")

        self.assertEqual(results_dir_expected, results_dir)

        shutil.rmtree(results_dir_expected)

    def test_results_create_correct_fullPath_dir(self):

        results_dir = os.path.join(os.getcwd(), "full_path", "test")
        results_dir = results(results_dir)
        results_dir_expected = os.path.join(os.getcwd(), "full_path", "test")

        self.assertEqual(results_dir_expected, results_dir)

        shutil.rmtree(results_dir_expected)
        os.rmdir(os.path.join(os.getcwd(), "full_path"))

    def test_groupResults_create_correct_group_results(self):

        results_dir = results(None)
        group_results_dir = group_results(results_dir, "test_group")
        group_results_dir_expected = os.path.join(results_dir, "test_group")

        self.assertEqual(group_results_dir_expected, group_results_dir)
        self.assertTrue(os.path.exists(group_results_dir_expected))

        shutil.rmtree(results_dir)

    def test_restablesDir_create_correct_random_dir(self):

        results_dir = results(None)
        group_name = 'random'

        tables_dir = restables_dir(results_dir, group_name)
        tables_dir_expected = os.path.join(results_dir, 'random')

        self.assertEqual(tables_dir_expected, tables_dir)
        self.assertTrue(os.path.exists(tables_dir_expected))

        shutil.rmtree(results_dir)

    def test_figures_create_correct_dir(self):

        results_dir = results(None)
        group_results_dir = group_results(results_dir, "test_group")

        figures_dir = figures(group_results_dir)
        figures_dir_expected = os.path.join(group_results_dir, 'support_pages',
                                            'figures')

        self.assertEqual(figures_dir_expected, figures_dir)
        self.assertTrue(os.path.exists(figures_dir_expected))

        shutil.rmtree(results_dir)


if __name__ == "__main__":
    unittest.main()
