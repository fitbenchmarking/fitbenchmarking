'''
Test fitting_report
'''

import inspect
import os
from tempfile import TemporaryDirectory
import unittest

import fitbenchmarking
from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.results_processing import fitting_report
from fitbenchmarking.utils.fitbm_result import FittingResult
from fitbenchmarking.utils.options import Options


class CreateTests(unittest.TestCase):
    '''
    Create tests for fitting_report
    '''

    def setUp(self):
        self.options = Options()
        cost_func = []
        for i in range(5):
            problem = FittingProblem(self.options)
            problem.name = f'prob {i}'
            problem.starting_values = [{'x': 1}]
            cost_func.append(NLLSCostFunc(problem))

        minimizers = ['min_a', 'min_b', 'min_c']
        self.results = [FittingResult(options=self.options,
                                      cost_func=c,
                                      jac='j1',
                                      hess=None,
                                      initial_params=[],
                                      params=[],
                                      minimizer=m,
                                      acc=1.0001,
                                      runtime=2.0002)
                        for m in minimizers
                        for c in cost_func]

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        # pylint: disable=consider-using-with
        self.dir = TemporaryDirectory(dir=root)
        # pylint: enable=consider-using-with

    def test_create_unique_files(self):
        """
        Tests that the create function creates a set of unique files.
        """
        fitting_report.create(results=self.results,
                              support_pages_dir=self.dir.name,
                              options=self.options)

        file_names = sorted([r.fitting_report_link
                             for r in self.results])

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

        minimizer = 'min_a'
        cost_func = NLLSCostFunc(problem)
        jac = 'j1'
        self.result = FittingResult(options=self.options,
                                    cost_func=cost_func,
                                    jac=jac,
                                    hess=None,
                                    initial_params=[],
                                    params=[],
                                    software='s1',
                                    minimizer=minimizer,
                                    acc=1.0001,
                                    runtime=2.0002)

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        # pylint: disable=consider-using-with
        self.dir = TemporaryDirectory(dir=root)
        # pylint: enable=consider-using-with

    def test_create_files(self):
        """
        Tests that files are created for each result.
        """
        fitting_report.create_prob_group(result=self.result,
                                         support_pages_dir=self.dir.name,
                                         options=self.options)
        self.assertTrue(os.path.exists(self.result.fitting_report_link))

    def test_file_name(self):
        """
        Tests that the filenames are in the expected form.
        """
        fitting_report.create_prob_group(result=self.result,
                                         support_pages_dir=self.dir.name,
                                         options=self.options)
        file_name = self.result.fitting_report_link
        expected = os.path.join(os.path.relpath(self.dir.name),
                                'prob_a_nllscostfunc_min_a_[s1]_jj1.html')

        self.assertEqual(file_name, expected)


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
        cost_func = NLLSCostFunc(problem)
        jac = 'j1'
        self.result = FittingResult(options=self.options,
                                    cost_func=cost_func,
                                    jac=jac,
                                    hess=None,
                                    initial_params=[],
                                    params=[],
                                    minimizer='test')

    def test_with_links(self):
        """
        Tests that the returned links are correct when links are passed in.
        """
        self.result.figure_link = 'some_link'
        self.result.start_figure_link = 'other_link'
        self.result.posterior_plots = 'another_link'
        figure_link, start_link, posterior_link = fitting_report.get_figure_paths(self.result)
        self.assertEqual(figure_link, os.path.join('figures', 'some_link'))
        self.assertEqual(start_link, os.path.join('figures', 'other_link'))
        self.assertEqual(posterior_link, os.path.join('figures', 'another_link'))

    def test_no_links(self):
        """
        Tests that links are not changed if an empty string is given.
        """
        self.result.figure_link = ''
        self.result.start_figure_link = ''
        self.result.posterior_plots = ''
        figure_link, start_link, posterior_link = fitting_report.get_figure_paths(self.result)
        self.assertEqual(figure_link, '')
        self.assertEqual(start_link, '')
        self.assertEqual(posterior_link, '')


if __name__ == "__main__":
    unittest.main()
