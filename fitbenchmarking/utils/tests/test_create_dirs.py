from __future__ import absolute_import, division, print_function

import time
import os
import shutil
import unittest

from fitbenchmarking.utils.create_dirs import (figures, group_results, results,
                                               support_pages, css)


class CreateDirsTests(unittest.TestCase):

    def setUp(self):
        path = 'r{}'.format(int(time.time()))
        self.results_dir = os.path.join(os.getcwd(), path)

    def tearDown(self):
        if os.path.exists(self.results_dir):
            shutil.rmtree(self.results_dir)

    def test_results_throw_correct_error(self):

        self.assertRaises(TypeError, results, 123)
        self.assertRaises(TypeError, results, None)

    def test_results_create_correct_dir(self):

        results_dir = results(self.results_dir)
        results_dir_expected = self.results_dir

        self.assertEqual(results_dir_expected, results_dir)
        self.assertTrue(os.path.exists(results_dir_expected))

        shutil.rmtree(results_dir_expected)

    def test_groupResults_create_correct_group_results(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")
        group_results_dir_expected = os.path.join(results_dir, "test_group")

        self.assertEqual(group_results_dir_expected, group_results_dir)
        self.assertTrue(os.path.exists(group_results_dir_expected))

        shutil.rmtree(results_dir)

    def test_support_pages_create_correct_dir(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")
        support_pages_dir = support_pages(group_results_dir)
        support_pages_dir_expected = os.path.join(group_results_dir,
                                                  'support_pages')

        self.assertEqual(support_pages_dir_expected, support_pages_dir)
        self.assertTrue(os.path.exists(support_pages_dir_expected))

        shutil.rmtree(results_dir)

    def test_figures_create_correct_dir(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")
        support_pages_dir = support_pages(group_results_dir)

        figures_dir = figures(support_pages_dir)
        figures_dir_expected = os.path.join(support_pages_dir, 'figures')

        self.assertEqual(figures_dir_expected, figures_dir)
        self.assertTrue(os.path.exists(figures_dir_expected))

        shutil.rmtree(results_dir)

    def test_css_create_correct_dir(self):

        results_dir = results(self.results_dir)
        group_results_dir = group_results(results_dir, "test_group")
        css_dir = css(group_results_dir)
        css_dir_expected = os.path.join(group_results_dir,
                                    'css')
        
        self.assertEqual(css_dir_expected, css_dir)
        self.assertTrue(os.path.exists(css_dir_expected))

        shutil.rmtree(css_dir)


if __name__ == "__main__":
    unittest.main()
