from __future__ import (absolute_import, division, print_function)
import inspect
import os
import shutil
import time
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils.misc import get_problem_files, combine_files


class CreateDirsTests(unittest.TestCase):

    def base_path(self):
        """
        Helper function that returns the path to
        /fitbenchmarking/benchmark_problems
        """
        bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
        return bench_prob_dir

    def setUp(self):
        """
        Create some datafiles to look for.
        """
        self.dirname = os.path.join(self.base_path(),
                                    'mock_datasets_{}'.format(time.time()))
        os.mkdir(self.dirname)

        expected = []
        for i in range(10):
            filename = 'file_{}.txt'.format(i)
            filepath = os.path.join(self.dirname, filename)
            expected.append(filepath)

            with open(filepath, 'w+') as f:
                f.write('This is a mock data file to check that finding files'
                        'is correct')

        self.expected = sorted(expected)

    def tearDown(self):
        """
        Clean up created datafiles.
        """
        shutil.rmtree(self.dirname)

    def test_getProblemFiles_get_correct_probs(self):
        """
        Test that the correct files are found
        """

        problems = get_problem_files(self.dirname)

        self.assertIsInstance(problems, list)
        self.assertEqual(self.expected, sorted(problems))


class CreateCombineFilesTests(unittest.TestCase):

    def setUp(self):
        """
        Create datafile directory.
        """
        self.dirname = "test_files"
        os.mkdir(self.dirname)

    def create_files(self, n):
        """
        Create some datafiles to look for.
        """
        self.expected_file = '{0}/expected_file.txt'.format(self.dirname)
        expected_message = ''
        self.files = []
        for i in range(n):
            datafile = '{0}/file_{1}.txt'.format(self.dirname, i)
            file_message = 'This is file number {}\n'.format(i)
            expected_message += '{0}'.format(file_message)
            with open(datafile, 'w+') as f:
                f.write(file_message)
            self.files.append(datafile)

        with open(self.expected_file, 'w+') as f:
            f.write(expected_message)

    def tearDown(self):
        """
        Clean up created datafiles.
        """
        shutil.rmtree(self.dirname)

    def test_combine_files_no_files(self):
        """
        Test that when no file is given an IndexError is raised
        """
        output_file = "output.txt"
        with self.assertRaises(IndexError):
            combine_files(output_file)

    def test_combine_files_multiple_files(self):
        """
        Test that the correct files are found
        """
        self.create_files(10)
        output_file = '{0}/output_file.txt'.format(self.dirname)
        combine_files(output_file, *self.files)
        with open(self.expected_file, 'r') as f:
            expected = f.readlines()
        with open(output_file, 'r') as f:
            actual = f.readlines()
        diff = []
        for i in range(len(expected)):
            if expected[i] != actual[i]:
                diff.append([expected[i], actual[i]])
        self.assertListEqual(expected, actual)

    def test_combine_files_wrong_name(self):
        """
        Test that wrong name file
        """
        output_file = "output.txt"
        with self.assertRaises(RuntimeError):
            combine_files(output_file, 'Wrong_file')


if __name__ == "__main__":
    unittest.main()
