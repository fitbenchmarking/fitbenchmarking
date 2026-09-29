from unittest import TestCase
from unittest.mock import ANY, Mock, patch

from parameterized import parameterized

import fitbenchmarking.utils.test_utils as test_utils


class CompareFilesTests(TestCase):
    def setUp(self):
        self.mock_test_case = Mock(spec=TestCase)

    @patch("builtins.open")
    def test_compare_files_when_files_match(self, file_io_mock):
        file = file_io_mock.return_value.__enter__.return_value
        file.readlines.return_value = [
            "This is a test file\n",
            "This file contains test data\n",
        ]
        actual_content = "This is a test file\nThis file contains test data\n"
        test_utils.compare_files(
            self.mock_test_case, "expected_output.txt", actual_content
        )
        self.mock_test_case.assertTrue.assert_called_once_with(True, msg=ANY)

    @patch("builtins.open")
    def test_compare_files_when_files_do_not_match(self, file_io_mock):
        file = file_io_mock.return_value.__enter__.return_value
        file.readlines.return_value = [
            "This is a test file\n",
            "This file contains test data\n",
        ]
        actual_content = (
            "This is a test file\nThis file contains different data\n"
        )
        test_utils.compare_files(
            self.mock_test_case, "expected_output.txt", actual_content
        )
        self.mock_test_case.assertTrue.assert_called_once_with(False, msg=ANY)

    @patch("builtins.open")
    def test_compare_files_with_custom_eq_when_files_match(self, file_io_mock):
        file = file_io_mock.return_value.__enter__.return_value
        file.readlines.return_value = [
            "This is a test file\n",
            "This file contains test data\n",
        ]
        actual_content = (
            "This is a test file\nThis file contains different test data\n"
        )

        def relaxed_comparator(lhs, rhs):
            return "test" in lhs and "test" in rhs

        test_utils.compare_files(
            self.mock_test_case,
            "expected_output.txt",
            actual_content,
            eq=relaxed_comparator,
        )
        self.mock_test_case.assertTrue.assert_called_once_with(True, msg=ANY)

    @patch("builtins.open")
    def test_compare_files_with_custom_eq_when_files_do_not_match(
        self, file_io_mock
    ):
        file = file_io_mock.return_value.__enter__.return_value
        file.readlines.return_value = [
            "This is a test file\n",
            "This file contains test data\n",
        ]
        actual_content = (
            "This is a test file\nThis file contains different data\n"
        )

        def strict_comparator(lhs, rhs):
            return lhs == rhs

        test_utils.compare_files(
            self.mock_test_case,
            "expected_output.txt",
            actual_content,
            eq=strict_comparator,
        )
        self.mock_test_case.assertTrue.assert_called_once_with(
            False,
            msg=ANY,
        )

    @parameterized.expand(
        [
            (
                "Windows",
                "This is a test file\r\nThis file contains test data\r\n",
            ),
            (
                "Linux",
                "This is a test file\nThis file contains test data\n",
            ),
            (
                "Darwin",
                "This is a test file\nThis file contains test data\n",
            ),
        ]
    )
    @patch("fitbenchmarking.utils.test_utils.platform.system")
    @patch("builtins.open")
    def test_compare_files_works_with_different_line_endings(
        self, platform_name, actual_content, file_io_mock, mock_platform
    ):
        mock_platform.return_value = platform_name
        file = file_io_mock.return_value.__enter__.return_value
        file.readlines.return_value = [
            "This is a test file\n",
            "This file contains test data\n",
        ]
        test_utils.compare_files(
            self.mock_test_case, "expected_output.txt", actual_content
        )
        self.mock_test_case.assertTrue.assert_called_once_with(True, msg=ANY)
