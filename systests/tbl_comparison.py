"""
Compares the current results with a set of expected results.
"""

import unittest
import os
import re
import numpy as np


class SystemTest(unittest.TestCase):
    def path_to_results(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        results_dir = os.path.join(current_dir, "results")

        return results_dir

    def path_to_expected_results_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        expected_results_dir = os.path.join(current_dir, "expected_results")

        return expected_results_dir

    def get_expected_results_paths_nist(self):
        expected_results_dir = self.path_to_expected_results_dir()
        nist_low_path = os.path.join(expected_results_dir, "nist_low_acc.txt")
        nist_avg_path = os.path.join(expected_results_dir, "nist_avg_acc.txt")
        nist_high_path = os.path.join(
            expected_results_dir, "nist_high_acc.txt")

        return nist_low_path, nist_avg_path, nist_high_path

    def read_expected_results_nist(self):
        nist_low_path, nist_average_path, nist_high_path = \
            self.get_expected_results_paths_nist()

        with open(nist_low_path) as file:
            nist_low = file.read()
        with open(nist_average_path) as file:
            nist_average = file.read()
        with open(nist_high_path) as file:
            nist_high = file.read()

        return nist_low, nist_average, nist_high

    def get_expected_results_paths_neutron(self):
        expected_results_dir = self.path_to_expected_results_dir()
        neutron_path = os.path.join(expected_results_dir, "neutron_acc.txt")

        return neutron_path

    def read_expected_results_neutron(self):
        neutron_path = self.get_expected_results_paths_neutron()

        with open(neutron_path) as file:
            neutron = file.read()
        return neutron

    def get_results_paths_nist(self):
        results_dir = self.path_to_results()

        nist_low_dir = os.path.join(results_dir, "NIST_low_difficulty")
        nist_average_dir = os.path.join(results_dir, "NIST_average_difficulty")
        nist_high_dir = os.path.join(results_dir, "NIST_high_difficulty")

        nist_low_path = \
            os.path.join(
                nist_low_dir, "NIST_low_difficulty_acc_weighted_table.txt")
        nist_average_path = \
            os.path.join(
                nist_average_dir,
                "NIST_average_difficulty_acc_weighted_table.txt")
        nist_high_path = \
            os.path.join(
                nist_high_dir, "NIST_high_difficulty_acc_weighted_table.txt")

        return nist_low_path, nist_average_path, nist_high_path

    def read_results_nist(self):
        nist_low_path, nist_average_path, nist_high_path = \
            self.get_results_paths_nist()

        with open(nist_low_path) as file:
            nist_low = file.read()
        with open(nist_average_path) as file:
            nist_average = file.read()
        with open(nist_high_path) as file:
            nist_high = file.read()

        return nist_low, nist_average, nist_high

    def get_results_paths_neutron(self):
        results_dir = self.path_to_results()
        neutron_tables_dir = os.path.join(results_dir, "Neutron_data")
        neutron_path = \
            os.path.join(
                neutron_tables_dir, "Neutron_data_acc_weighted_table.txt")

        return neutron_path

    def read_results_neutron(self):
        neutron_path = self.get_results_paths_neutron()

        with open(neutron_path) as file:
            neutron = file.read()

        return neutron

    def string_to_np_table(self, string_tbl):
        strings = re.findall("(?<=\\`)(?:[0-9]*[.])?[0-9]+(?=\\`)", string_tbl)
        np_table = np.array(strings)
        np_table = np_table.astype(np.float)

        return np_table

    def nist_expected_results_np_tables(self):
        expected_results = self.read_expected_results_nist()
        nist_low = self.string_to_np_table(expected_results[0])
        nist_avg = self.string_to_np_table(expected_results[1])
        nist_high = self.string_to_np_table(expected_results[2])

        return nist_low, nist_avg, nist_high

    def nist_results_np_tables(self):
        results = self.read_results_nist()
        nist_low = self.string_to_np_table(results[0])
        nist_avg = self.string_to_np_table(results[1])
        nist_high = self.string_to_np_table(results[2])

        return nist_low, nist_avg, nist_high

    def neutron_expected_results_np_tables(self):
        expected_results = self.read_expected_results_neutron()
        neutron = self.string_to_np_table(expected_results)

        return neutron

    def neutron_results_np_tables(self):
        results = self.read_results_neutron()
        neutron = self.string_to_np_table(results)

        return neutron

    def test_nist(self):
        expected_results = self.nist_expected_results_np_tables()
        results = self.nist_results_np_tables()

        np.testing.assert_allclose(results[0], expected_results[0], 3)
        np.testing.assert_allclose(results[1], expected_results[1], 3)
        np.testing.assert_allclose(results[2], expected_results[2], 3)

    def test_neutron(self):
        expected_results = self.neutron_expected_results_np_tables()
        results = self.neutron_results_np_tables()

        np.testing.assert_allclose(expected_results, results, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
