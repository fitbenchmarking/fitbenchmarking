from __future__ import (absolute_import, division, print_function)

import inspect
import os
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import unittest

import fitbenchmarking
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.jacobian.SciPyFD_2point_jacobian import ScipyTwoPoint
from fitbenchmarking.results_processing import support_page
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class CreateTests(unittest.TestCase):

    def setUp(self):
        self.options = Options()
        problems = []
        for i in range(5):
            problem = FittingProblem(self.options)
            problem.name = 'prob {}'.format(i)
            problem.starting_values = [{'x': 1}]
            problems.append(problem)

        minimizers = ['min_a', 'min_b', 'min_c']
        self.results = [[FittingResult(options=self.options,
                                       problem=p,
                                       jac=ScipyTwoPoint(p),
                                       initial_params=[],
                                       params=[],
                                       minimizer=m)
                         for m in minimizers]
                        for p in problems]
        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        self.dir = TemporaryDirectory(dir=root)

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


class CreateProbGroupTests(unittest.TestCase):
    """
    Tests that the correct files are created by group tests.
    Does not test the content of the file currently.
    """

    def setUp(self):
        self.options = Options()
        problem = FittingProblem(self.options)
        problem.name = 'prob a'
        problem.equation = 'equation!'
        problem.starting_values = [{'x': 1}]

        minimizers = ['min_a', 'min_b', 'min_c']
        self.results = [FittingResult(options=self.options,
                                      problem=problem,
                                      jac=ScipyTwoPoint(problem),
                                      initial_params=[],
                                      params=[],
                                      minimizer=m)
                        for m in minimizers]

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        self.dir = TemporaryDirectory(dir=root)

    def test_create_files(self):
        """
        Tests that files are created for each result.
        """
        support_page.create_prob_group(prob_results=self.results,
                                       group_name='test_group',
                                       support_pages_dir=self.dir.name,
                                       options=self.options)
        self.assertTrue(all(
            os.path.exists(r.support_page_link) for r in self.results))

    def test_file_name(self):
        """
        Tests that the filenames are in the expected form.
        """
        support_page.create_prob_group(prob_results=self.results,
                                       group_name='test_group',
                                       support_pages_dir=self.dir.name,
                                       options=self.options)
        file_names = [r.support_page_link for r in self.results]
        expected = [os.path.join(os.path.relpath(self.dir.name), f)
                    for f in ['test_group_prob_a_min_a.html',
                              'test_group_prob_a_min_b.html',
                              'test_group_prob_a_min_c.html']]

        self.assertListEqual(file_names, expected)


class GetFigurePathsTests(unittest.TestCase):
    """
    Tests the very simple get_figure_paths function
    """

    def setUp(self):
        self.options = Options()
        problem = FittingProblem(self.options)
        problem.name = 'prob a'
        problem.equation = 'equation!'
        problem.starting_values = [{'x': 1}]
        self.result = FittingResult(options=self.options,
                                    problem=problem,
                                    jac=ScipyTwoPoint(problem),
                                    initial_params=[],
                                    params=[],
                                    minimizer='test')

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
