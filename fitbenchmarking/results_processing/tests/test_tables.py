"""
Table tests
"""

import inspect
import os
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
                    "emissions": "pp_3",
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
                "emissions": "pp_3",
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

    def compare_files(self, expected, achieved):
        """
        Compares two files line by line

        :param expected: imported HTML output from expected results in
                         fitbenchmarking/results_processing/tests/
                         expected_results
        :type expected: str
        :param achieved: HTML generated using generate_table in
                         fitbenchmarking.results_processing.tables
        :type achieved: str
        """
        with open(expected, encoding="utf-8") as f:
            exp_lines = f.readlines()

        diff = []
        for i, (act_line, exp_line) in enumerate(
            zip(achieved.splitlines(), exp_lines)
        ):
            exp_line = "" if exp_line is None else exp_line.strip("\n")
            act_line = "" if act_line is None else act_line.strip("\n")
            # to pass on windows need to first do this before comparing
            act_line = act_line.replace('href="..\\', 'href="../')
            if act_line != exp_line:
                diff.append([i, exp_line, act_line])
        if diff:
            print(
                f"Comparing against {expected}\n"
                + "\n".join(
                    [
                        f"== Line {change[0]} ==\n"
                        f"Expected :{change[1]}\n"
                        f"Actual   :{change[2]}"
                        for change in diff
                    ]
                )
            )
            print("\n==\n")
            print("Output generated (also saved as actual.out):")
            print(achieved)
            with open("actual.out", "w", encoding="utf-8") as outfile:
                outfile.write(achieved)
        self.assertListEqual([], diff)


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
                "emissions": "pp_3",
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
