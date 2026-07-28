"""
Table tests
"""

import difflib
import inspect
import os
import platform
import shutil
import unittest
from inspect import getfile

import fitbenchmarking
from fitbenchmarking import test_files
from fitbenchmarking.core.results_output import preprocess_data
from fitbenchmarking.results_processing.tables import (
    SORTED_TABLE_NAMES,
    create_results_tables,
    generate_table,
)
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import Options


def load_mock_results():
    """
    Load a predictable results set.

    :return: Manually generated results
    :rtype: list[FittingResult]
    """
    options = Options()
    cp_dir = os.path.dirname(inspect.getfile(test_files))
    options.checkpoint_filename = os.path.join(cp_dir, "checkpoint.json")

    cp = Checkpoint(options)
    results, _, _, _ = cp.load()
    results = results["Fake_Test_Data"]
    for i, r in enumerate(results):
        r.fitting_report_link = f"link{i}"
        r.problem_summary_page_link = "link0"

    return results


class GenerateTableTests(unittest.TestCase):
    """
    Class that tests the generate_table function within
    fitbenchmarking.results_processing.tables
    """

    maxDiff = None

    def setUp(self):
        """
        Setup up method for test
        """
        results = load_mock_results()
        self.best_results, self.results = preprocess_data(results)

        self.options = Options()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.expected_results_dir = os.path.join(
            root, "results_processing", "tests", "expected_results"
        )

        self.fig_dir = os.path.join(
            root, "results_processing", "tests", "figures"
        )
        if not os.path.exists(self.fig_dir):
            os.mkdir(self.fig_dir)

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.fig_dir):
            shutil.rmtree(self.fig_dir)

    def test_tables_correct(self):
        """
        Test that the tables are equal to the expected output stored in
        fitbenchmarking/results_processing/tests/expected_results
        """
        for suffix in SORTED_TABLE_NAMES:
            _, html, csv_table, _ = generate_table(
                results=self.results,
                best_results=self.best_results,
                options=self.options,
                group_dir="group_dir",
                fig_dir=self.fig_dir,
                pp_locations={
                    "acc": "pp_1",
                    "energy_usage": "pp_3",
                    "runtime": "pp_2",
                },
                table_name="table_name",
                suffix=suffix,
            )

            html_table_name = os.path.join(
                self.expected_results_dir, f"{suffix}.html"
            )
            csv_table_name = os.path.join(
                self.expected_results_dir, f"{suffix}.csv"
            )
            for f, t in zip(
                [html_table_name, csv_table_name], [html["table"], csv_table]
            ):
                self.compare_files(f, t)

    def test_dropdown_html_correct(self):
        """
        Test that the HTML for dropdown menus used for hiding/showing
        table rows and columns is generated as expected.
        """
        _, html, _, _ = generate_table(
            results=self.results,
            best_results=self.best_results,
            options=self.options,
            group_dir="group_dir",
            fig_dir=self.fig_dir,
            pp_locations={
                "acc": "pp_1",
                "energy_usage": "pp_3",
                "runtime": "pp_2",
            },
            table_name="table_name",
            suffix="compare",
        )

        expected_problem_dropdown = os.path.join(
            self.expected_results_dir, "problem_dropdown.html"
        )
        expected_minimizer_dropdown = os.path.join(
            self.expected_results_dir, "minimizer_dropdown.html"
        )

        for expected_file, dropdown_name in zip(
            [expected_problem_dropdown, expected_minimizer_dropdown],
            ["problem_dropdown", "minim_dropdown"],
        ):
            self.compare_files(expected_file, html[dropdown_name])

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


class CreateResultsTableTests(unittest.TestCase):
    """
    Class that tests the generate_table function within
    fitbenchmarking.results_processing.create_results_tables
    """

    def setUp(self):
        """
        Setup up method for test
        """
        results = load_mock_results()
        self.best_results, self.results = preprocess_data(results)

        self.options = Options()
        root = os.path.dirname(getfile(fitbenchmarking))

        self.group_dir = os.path.join(
            root, "results_processing", "tests", "results"
        )

        if not os.path.exists(self.group_dir):
            os.mkdir(self.group_dir)

        self.fig_dir = os.path.join(
            root, "results_processing", "tests", "figures"
        )
        os.mkdir(self.fig_dir)

        self.group_name = "test_name"

    def tearDown(self):
        """
        Deletes temporary folder and results produced
        """
        if os.path.exists(self.group_dir):
            shutil.rmtree(self.group_dir)

        if os.path.exists(self.fig_dir):
            shutil.rmtree(self.fig_dir)

    def test_generate_table_page(self):
        """
        Checks to see whether files with the correct name are produced.
        """
        create_results_tables(
            options=self.options,
            results=self.results,
            best_results=self.best_results,
            group_dir=self.group_dir,
            fig_dir=self.fig_dir,
            pp_locations={
                "acc": "pp_1",
                "energy_usage": "pp_3",
                "runtime": "pp_2",
            },
            failed_problems=[],
            unselected_minimzers={"min1": []},
        )
        for suffix in SORTED_TABLE_NAMES:
            for table_type in ["html", "csv"]:
                table_name = f"{suffix}_table.{table_type}"
                file_name = os.path.join(self.group_dir, table_name)
                self.assertTrue(
                    os.path.isfile(file_name), f"Could not find {file_name}"
                )


if __name__ == "__main__":
    unittest.main()
