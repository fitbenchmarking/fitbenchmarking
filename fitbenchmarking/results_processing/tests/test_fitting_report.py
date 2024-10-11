"""
Test fitting_report
"""

import inspect
import os
import unittest
from tempfile import TemporaryDirectory

import fitbenchmarking
from fitbenchmarking import test_files
from fitbenchmarking.results_processing import fitting_report
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options


def load_mock_results():
    """
    Load a predictable set of results.

    :return: Set of manually generated results
    :rtype: list[FittingResult]
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, "checkpoint.json")

    cp = Checkpoint(options)
    results, _, _ = cp.load()

    return [r for r in results["Fake_Test_Data"] if r.problem_tag == "prob_0"]


class CreateTests(unittest.TestCase):
    """
    Create tests for fitting_report
    """

    def setUp(self):
        self.results = load_mock_results()
        self.options = Options()

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        self.dir = TemporaryDirectory(dir=root)

    def test_create_unique_files(self):
        """
        Tests that the create function creates a set of unique files.
        """
        fitting_report.create(
            results=self.results,
            support_pages_dir=self.dir.name,
            options=self.options,
        )

        file_names = sorted([r.fitting_report_link for r in self.results])

        unique_names = sorted(list(set(file_names)))

        self.assertListEqual(unique_names, file_names)


class CreateProbGroupTests(unittest.TestCase):
    """
    Tests that the correct files are created by group tests.
    Does not test the content of the file currently.
    """

    def setUp(self):
        self.options = Options()
        self.result = load_mock_results()[0]

        root = os.path.dirname(inspect.getfile(fitbenchmarking))
        self.dir = TemporaryDirectory(dir=root)

    def test_create_files(self):
        """
        Tests that files are created for each result.
        """
        fitting_report.create_prob_group(
            result=self.result,
            support_pages_dir=self.dir.name,
            options=self.options,
        )
        self.assertTrue(os.path.exists(self.result.fitting_report_link))

    def test_file_name(self):
        """
        Tests that the filenames are in the expected form.
        """
        fitting_report.create_prob_group(
            result=self.result,
            support_pages_dir=self.dir.name,
            options=self.options,
        )
        file_name = self.result.fitting_report_link
        expected = os.path.abspath(
            os.path.join(self.dir.name, "prob_0_cf1_m10_[s1]_jj0.html")
        )

        self.assertEqual(file_name, expected)


class GetFigurePathsTests(unittest.TestCase):
    """
    Tests the very simple get_figure_paths function
    """

    def setUp(self):
        self.options = Options()
        self.result = load_mock_results()[0]

    def test_with_links(self):
        """
        Tests that the returned links are correct when links are passed in.
        """
        self.result.figure_link = "some_link"
        self.result.start_figure_link = "other_link"
        self.result.posterior_plots = "another_link"
        figure_link, start_link, posterior_link = (
            fitting_report.get_figure_paths(self.result)
        )
        self.assertEqual(figure_link, os.path.join("figures", "some_link"))
        self.assertEqual(start_link, os.path.join("figures", "other_link"))
        self.assertEqual(
            posterior_link, os.path.join("figures", "another_link")
        )

    def test_no_links(self):
        """
        Tests that links are not changed if an empty string is given.
        """
        self.result.figure_link = ""
        self.result.start_figure_link = ""
        self.result.posterior_plots = ""
        figure_link, start_link, posterior_link = (
            fitting_report.get_figure_paths(self.result)
        )
        self.assertEqual(figure_link, "")
        self.assertEqual(start_link, "")
        self.assertEqual(posterior_link, "")


if __name__ == "__main__":
    unittest.main()
