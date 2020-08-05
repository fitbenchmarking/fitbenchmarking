from __future__ import (absolute_import, division, print_function)
import unittest
import os
import shutil

from fitbenchmarking.core.results_output import create_directories
from fitbenchmarking.utils.options import Options


class SaveResultsTests(unittest.TestCase):
    def test_dummy(self):
        """
        Dummy test to appease pytest
        """
        pass


class CreateDirectoriesTests(unittest.TestCase):
    """
    Unit tests for create_directories function
    """

    def setUp(self):
        """
        Setting up paths and results folders
        """
        self.options = Options()
        test_path = os.path.dirname(os.path.realpath(__file__))
        self.dirname = os.path.join(test_path, 'results')
        os.mkdir(self.dirname)

    def tearDown(self):
        """
        Clean up created folders.
        """
        shutil.rmtree(self.dirname)

    def test_create_dirs_correct(self):
        """
        Dummy test to appease pytest
        """
        group_name = 'test_group'
        self.options.results_dir = self.dirname
        expected_results_dir = self.dirname
        expected_group_dir = os.path.join(expected_results_dir, group_name)
        expected_support_dir = os.path.join(expected_group_dir,
                                            'support_pages')
        expected_figures_dir = os.path.join(expected_support_dir, 'figures')

        results_dir, group_dir, support_dir, figures_dir = \
            create_directories(self.options, group_name)

        assert results_dir == expected_results_dir
        assert group_dir == expected_group_dir
        assert support_dir == expected_support_dir
        assert figures_dir == expected_figures_dir

        assert os.path.isdir(results_dir)
        assert os.path.isdir(group_dir)
        assert os.path.isdir(support_dir)
        assert os.path.isdir(figures_dir)


class PreproccessDataTests(unittest.TestCase):
    def test_dummy(self):
        """
        Dummy test to appease pytest
        """
        pass


class CreatePlotsTests(unittest.TestCase):
    def test_dummy(self):
        """
        Dummy test to appease pytest
        """
        pass


class CreateProblemLevelIndex(unittest.TestCase):
    def test_dummy(self):
        """
        Dummy test to appease pytest
        """
        pass


if __name__ == "__main__":
    unittest.main()
