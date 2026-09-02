import difflib
import os
import platform
import unittest
from collections.abc import Callable


def compare_files(
    test_case: unittest.TestCase,
    expected_output_file: str,
    actual_output: str,
    eq: Callable | None = None,
):
    """
    Compares two files line by line, if they do not match, output a git
    style unified diff to actual.diff and the actual output to actual.out

    :param test_case: The test case instance executing the assertion
    :type test_case: unittest.TestCase
    :param expected_output_file: path to a file containing the expected
        output. Typically found at results_processing/tests/expected_results
    :type expected_output_file: str

    :param actual_output: a string containing the actual output generated
        when the test was run.
    :type actual_output: str
    :param eq: A function that returns True if two lines match.
        Useful for comparing regression output with float
        tolerances.
    :type eq: callable, optional
    """

    with open(expected_output_file, encoding="utf-8") as f:
        expected_output_lines = f.readlines()

    out_file_dir = os.getcwd() + "/actual.out"
    diff_file_dir = os.getcwd() + "/actual.diff"

    # test files are generated on a Linux system, we need to make some
    # edits before running any comparisons if we are on windows
    if platform.system() == "Windows":
        actual_output = actual_output.replace('href="..\\', 'href="../')
        actual_output = actual_output.replace("\r\n", "\n")

    actual_output_lines = actual_output.splitlines(keepends=True)

    if eq:
        # if a matching function has been defined (e.g. to compare floats with
        # a tolerance) then use that function to compare the lines.
        # If two lines match under the custom comparator `eq`, we replace the
        # actual line with the expected line in this pre-processing step.
        # This ensures that `difflib.unified_diff` treats them as identical,
        # so only genuine mismatches exceeding tolerance are highlighted.
        try:
            from itertools import zip_longest
        except ImportError:
            from itertools import izip_longest as zip_longest
        actual_output_lines = [
            exp
            if exp is not None and act is not None and eq(exp, act)
            else act
            for exp, act in zip_longest(
                expected_output_lines, actual_output_lines
            )
        ]

    diff = list(
        difflib.unified_diff(
            expected_output_lines,
            actual_output_lines,
            fromfile=expected_output_file,
            tofile=out_file_dir,
        )
    )

    if len(diff) > 0:
        with open("actual.out", "w", encoding="utf-8") as out_file:
            out_file.write(actual_output)
        with open("actual.diff", "w", encoding="utf-8") as diff_file:
            diff_file.write("".join(diff))

    test_case.assertTrue(
        diff == [],
        msg=(
            f"{''.join(diff)}"
            "\n\n"
            "The output provided did not match the expected output from:"
            f" {expected_output_file}\n"
            f"The actual output has been saved in {out_file_dir}\n"
            f"full diff saved in {diff_file_dir}"
        ),
    )
