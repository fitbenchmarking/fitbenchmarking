from __future__ import (absolute_import, division, print_function)

import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import unittest

from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import support_page
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class CreateTests(unittest.TestCase):

    def setUp(self):
        self.options = Options()
        problems = []
        for _ in range(2):
            problem = FittingProblem()
            problem.sanitised_name = 'problem'
            problems.append(problem)
        for i in range(5):
            problem = FittingProblem()
            problem.sanitised_name = 'prob_{}'.format(i)
            problems.append(problem)

        minimizers = ['min_a', 'min_b', 'min_c']
        self.results = [[FittingResult(options=self.options,
                                       problem=p,
                                       minimizer=m)
                         for m in minimizers]
                        for p in problems]

        self.dir = TemporaryDirectory()

    def test_create_unique_files(self):
        """
        Tests that the create function creates a set of unique files.
        """
        support_page.create(results_per_test=self.results,
                            group_name='test_group',
                            support_pages_dir=self.dir.name,
                            options=self.options)

        file_names = sorted([r.support_page_link
                             for pr in self.results
                             for r in pr])

        unique_names = sorted(list(set(file_names)))

        self.assertListEqual(unique_names, file_names)

    def test_count_correct(self):
        """
        Tests that files are generated with the correct name.
        """

        support_page.create(results_per_test=self.results,
                            group_name='test_group',
                            support_pages_dir=self.dir.name,
                            options=self.options)

        file_names = [r.support_page_link
                      for pr in self.results
                      for r in pr]

        self.assertIn(
            os.path.join(self.dir.name, 'test_group_problem_1_min_a.html'),
            file_names)
        self.assertIn(
            os.path.join(self.dir.name, 'test_group_problem_2_min_a.html'),
            file_names)


class CreateProbGroupTests(unittest.TestCase):
    """
    Tests that the correct files are created by group tests.
    Does not test the content of the file currently.
    """
    def setUp(self):
        self.options = Options()
        problem = FittingProblem()
        problem.sanitised_name = 'prob_a'
        problem.equation = 'equation!'

        minimizers = ['min_a', 'min_b', 'min_c']
        self.results = [FittingResult(options=self.options,
                                      problem=problem,
                                      minimizer=m)
                        for m in minimizers]

        self.dir = TemporaryDirectory()

    def test_create_files(self):
        """
        Tests that files are created for each result.
        """
        support_page.create_prob_group(prob_results=self.results,
                                       group_name='test_group',
                                       support_pages_dir=self.dir.name,
                                       count=1,
                                       options=self.options)

        self.assertTrue(all(
            os.path.exists(os.path.join(self.dir.name, r.support_page_link))
            for r in self.results))

    def test_file_name(self):
        """
        Tests that the filenames are in the expected form.
        """
        support_page.create_prob_group(prob_results=self.results,
                                       group_name='test_group',
                                       support_pages_dir=self.dir.name,
                                       count=1,
                                       options=self.options)
        file_names = [r.support_page_link for r in self.results]
        expected = [os.path.join(self.dir.name, f)
                    for f in ['test_group_prob_a_1_min_a.html',
                              'test_group_prob_a_1_min_b.html',
                              'test_group_prob_a_1_min_c.html']]
        self.assertListEqual(file_names, expected)


class GetFigurePathsTests(unittest.TestCase):
    """
    Tests the very simple get_figure_paths function
    """
    def setUp(self):
        self.result = FittingResult()

    def test_with_links(self):
        """
        Tests that the returned links are correct when links are passed in.
        """
        self.result.figure_link = 'some_link'
        self.result.start_figure_link = 'other_link'
        figure_link, start_link = support_page.get_figure_paths(self.result)
        self.assertEqual(figure_link, os.path.join('figures', 'some_link'))
        self.assertEqual(start_link, os.path.join('figures', 'other_link'))

    def test_no_links(self):
        """
        Tests that links are not changed if an empty string is given.
        """
        self.result.figure_link = ''
        self.result.start_figure_link = ''
        figure_link, start_link = support_page.get_figure_paths(self.result)
        self.assertEqual(figure_link, '')
        self.assertEqual(start_link, '')


if __name__ == "__main__":
    unittest.main()
