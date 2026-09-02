# diff between html
# diff between dash tree

import difflib
import os
import platform


def compare_files(self, expected_output_file: str, actual_output: str):
    """
    Compares two files line by line, if they do not match, output a git
    style unified diff to actual.diff and the actual output to actual.out

    :param expected_output_file: path to a file containing the expected
    output. Typically found at results_processing/tests/expected_results
    :type expected_output_file: str

    :param actual_output: a string containing the actual output generated
    when the test was run.
    :type actual_output: str
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

    self.assertListEqual(
        [],
        diff,
        msg=(
            "\n\n"
            "The output provided did not match the expected output from:"
            f" {expected_output_file}\n"
            f"The actual output has been saved in {out_file_dir}\n"
            f"full diff saved in {diff_file_dir}"
        ),
    )
