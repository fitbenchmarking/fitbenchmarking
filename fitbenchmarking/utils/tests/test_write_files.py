"""
This file contains tests for the write files utils
"""

import os
import shutil
import unittest

from fitbenchmarking.utils.create_dirs import results
from fitbenchmarking.utils.exceptions import FilepathTooLongError
from fitbenchmarking.utils.write_files import CHARACTER_LIMIT, write_file


@write_file
def write_to_a_file(file_path: str, content: str):
    """
    Writes to a file using the provided file path and contents.

    :param file_path: path to a file.
    :type file_path: str
    :param content: the content of the file.
    :type content: str
    """
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


class WriteFilesTests(unittest.TestCase):
    """
    Tests for the write files decorator.
    """

    def setUp(self):
        """
        Creates a temporary directory in which files are stored
        """
        self.results_dir = os.path.join(os.getcwd(), "write_files_test")
        # Create a directory
        results(self.results_dir)

    def tearDown(self):
        """
        Deletes the temporary folder
        """
        if os.path.exists(self.results_dir):
            shutil.rmtree(self.results_dir)

    def test_exception_when_the_file_path_is_too_large(self):
        """
        Check that an exception is raised when the file path is too large.
        """
        file_path = os.path.join(self.results_dir, "very_" * 50, "long_filename.txt")
        self.assertGreater(len(file_path), CHARACTER_LIMIT)

        with self.assertRaises(FilepathTooLongError):
            write_to_a_file(file_path, "Hello")

        self.assertTrue(not os.path.exists(file_path))

    def test_a_file_exists_when_the_file_path_is_short(self):
        """
        Check that a file is created when the file path is short.
        """
        file_path = os.path.join(self.results_dir, "short_filename.txt")
        self.assertLess(len(file_path), CHARACTER_LIMIT)

        write_to_a_file(file_path, "Hello")

        self.assertTrue(os.path.exists(file_path))


if __name__ == "__main__":
    unittest.main()
