"""
Tests for checkpoint_handler.py
"""
import inspect
import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from fitbenchmarking import test_files
from fitbenchmarking.cli.checkpoint_handler import (generate_report, merge,
                                                    merge_data_sets,
                                                    merge_problems,
                                                    merge_results)


class TestGenerateReport(TestCase):
    """
    Simple testing for the checkpoint_handler generate report entry point
    """

    def test_no_checkpoint(self):
        """
        Test functionality when the provided checkpoint doesn't exist
        """
        options = {'checkpoint_filename': 'not_a_real_file',
                   'results_browser': False,
                   'external_output': 'debug'}

        with self.assertRaises(SystemExit):
            generate_report(additional_options=options)

    def test_create_files(self):
        """
        Tests expected files are created from the checkpoint.
        """
        cp_dir = Path(inspect.getfile(test_files)).parent
        cp_file = cp_dir / 'checkpoint.json'
        options = {'checkpoint_filename': str(cp_file),
                   'results_browser': False,
                   'external_output': 'debug'}

        # Random files from each directory that should be created
        expected = [
            'css/table_style.css',
            'fonts/FiraSans/woff2/FiraSans-Bold.woff2',
            'js/dropdown.js',
            'results_index.html',
            'Fake_Test_Data/compare_table.csv',
            'Fake_Test_Data/runtime_table.html',
            'Fake_Test_Data/support_pages/prob_0_summary.html',
            'Fake_Test_Data/support_pages/prob_0_cf1_m01_[s0]_jj0.html',
            'Fake_Test_Data/support_pages/figures/acc_cbar.png',
            'Fake_Test_Data/support_pages/figures/start_for_prob_0.png',
        ]

        with TemporaryDirectory() as results_dir:
            results = Path(results_dir)
            options['results_dir'] = results_dir
            generate_report(additional_options=options)

            print(f'Files in {results_dir} ({results})')
            for filename in results.iterdir():
                print(filename)
            print('Done')

            for e in expected:
                with self.subTest(f'Testing existance of "{e}"'):
                    file = results / e
                    assert file.exists(), f'Failed to find "{e}"'
                    assert file.stat().st_size > 0, f'File is empty: "{e}"'


class TestMergeDataSets(TestCase):
    """
    Simple testing for the checkpoint_handler merge entry point.
    Uses the definition of identical defined in the docstring of
    merge_data_sets
    """

    def setUp(self):
        """
        Generate 3 files to merge
        """
        ch_test_files = Path(__file__).parent / 'test_files'
        self.A = str(ch_test_files/'A.json')
        self.B = str(ch_test_files/'B.json')
        self.C = str(ch_test_files/'C.json')
        self.expected = ch_test_files / 'AB.json'
        self._dir = TemporaryDirectory()  # pylint:disable=consider-using-with
        self.dir = Path(self._dir.name)

    def test_create_new_file(self):
        """
        Test that a new checkpoint file is generated.
        """
        output = self.dir / 'out.json'
        merge_data_sets([self.A, self.B, self.C], str(output))
        assert output.exists(), f'No new checkpoint file {output}'

    def test_three_files(self):
        """
        Test that merging A, B, and C is the same as merging A and B, then
        merging the result with C.
        """
        intermediate = self.dir / 'intermediate.json'
        merge_data_sets([self.A, self.B], str(intermediate.absolute()))
        twomerge = self.dir / 'two-merges.json'
        merge_data_sets([str(intermediate), self.C], str(twomerge))
        onemerge = self.dir / 'one-merge.json'
        merge_data_sets([self.A, self.B, self.C], str(onemerge))

        errors = []
        for i, (l1, l2) in enumerate(zip(onemerge.read_text().splitlines(),
                                         twomerge.read_text().splitlines())):
            if l1 != l2:
                errors.append((i, l1, l2))

        assert not errors, 'Files do not match. ' \
            f'Lines {", ".join([str(e[0]) for e in errors])} disagree.'

    def test_regression_two_files(self):
        """
        Test that merging 2 files gives the expected output file.
        """
        output = self.dir / 'AB.json'
        merge_data_sets([self.A, self.B], str(output))

        errors = []
        for i, (l1, l2) in enumerate(
            zip(self.expected.read_text().splitlines(),
                output.read_text().splitlines())):
            if l1 != l2:
                errors.append((i, l1, l2))

        assert not errors, 'Files do not match. ' \
            f'Lines {", ".join([str(e[0]) for e in errors])} disagree.'

    def test_strategy_first(self):
        output = self.dir / 'AB.json'
        merge_data_sets([self.A, self.B], output=str(output), strategy='first')

        output_json = json.loads(output.read_text())
        merged_result = [r['accuracy']
                         for r in output_json['DataSet1']['results']
                         if r['name'] == 'prob_0'
                         and r['software_tag'] == 'common1']

        assert merged_result[0] == 0.1

    def test_strategy_last(self):
        output = self.dir / 'AB.json'
        merge_data_sets([self.A, self.B], output=str(output), strategy='last')

        output_json = json.loads(output.read_text())
        merged_result = [r['accuracy']
                         for r in output_json['DataSet1']['results']
                         if r['name'] == 'prob_0'
                         and r['software_tag'] == 'common1']

        assert merged_result[0] == 12.0

    def test_strategy_accuracy(self):
        output = self.dir / 'AB.json'
        merge_data_sets([self.A, self.B], output=str(output), strategy='accuracy')

        output_json = json.loads(output.read_text())
        merged_result = [r['accuracy']
                         for r in output_json['DataSet1']['results']
                         if r['name'] == 'prob_0'
                         and r['software_tag'] == 'common1']

        assert merged_result[0] == 0.1

    def test_strategy_runtime(self):
        output = self.dir / 'AB.json'
        merge_data_sets([self.A, self.B], output=str(output), strategy='runtime')

        output_json = json.loads(output.read_text())
        merged_result = [r['accuracy']
                         for r in output_json['DataSet1']['results']
                         if r['name'] == 'prob_0'
                         and r['software_tag'] == 'common1']

        assert merged_result[0] == 0.1


class TestMerge(TestCase):
    """
    Tests for the merge function.
    """

    def setUp(self):
        """
        Generate 4 datasets (A, B, C, and D) such that:
        - A and B and C have the same label
        - D has a unique label
        - A and B have 2 problems in common and 1 problem not in common
        - A and B have results for 2 softwares, only one of which is common
          between them
        - Problems in A and C have matching names but not matching data
        """
        ch_test_files = Path(__file__).parent / 'test_files'
        self.A = json.load((ch_test_files/'A.json').open())
        self.B = json.load((ch_test_files/'B.json').open())
        self.C = json.load((ch_test_files/'C.json').open())
        self.D = json.load((ch_test_files/'D.json').open())

    def test_merge_distinct_datasets(self):
        """
        Test that merging two datasets results in the catenation of them.
        """
        in_keys = list(self.A.keys()) + list(self.D.keys())
        M = merge(deepcopy(self.A), deepcopy(self.D))

        assert sorted(M.keys()) == sorted(in_keys), 'Datasets do not match'

    def test_problem_names_match(self):
        """
        Test that results are correctly labelled when problem renaming occurs.
        """
        M = merge(deepcopy(self.A), deepcopy(self.C))
        with self.subTest('number of problems'):
            assert len(M['DataSet1']['problems']) == 6, \
                'Merge resulted in wrong number of problems:' \
                f'{", ".join(M["DataSet1"]["problems"])}'
        with self.subTest('result name update'):
            assert M['DataSet1']['results'][6]['name'] == "prob_0*", \
                'Expected result name to be updated: '\
                f'{M["DataSet1"]["results"][6]}'


class TestMergeProblems(TestCase):
    """
    Tests for the merge_problems function
    """

    def setUp(self):
        """
        Generate 4 datasets (A, B, C) such that:
        - A and B and C have the same label
        - A and B have 2 problems in common and 1 problem not in common
        - A and B have results for 2 softwares, only one of which is common
          between them
        - Problems in A and C have matching names but not matching data
        """
        ch_test_files = Path(__file__).parent / 'test_files'
        self.A = json.load((ch_test_files/'A.json').open()
                           )['DataSet1']['problems']
        self.B = json.load((ch_test_files/'B.json').open()
                           )['DataSet1']['problems']
        self.C = json.load((ch_test_files/'C.json').open()
                           )['DataSet1']['problems']

    def test_merged_problems_subset_of_input(self):
        """
        Test that each problem in the merged result is in at least one of the
        inputs.
        """
        inputs = set(list(self.A)).union(set(list(self.B)))
        M, _ = merge_problems(self.A, self.B)
        M_set_norename = set(m.rstrip('*') for m in M.keys())
        assert M_set_norename.issubset(inputs), \
            'Merged result contains unexpected problem name'

    def test_merged_problems_superset_of_input(self):
        """
        Test that each problem in the inputs is in the merged result.
        """
        inputs = set(list(self.A)).union(set(list(self.B)))
        M, _ = merge_problems(self.A, self.B)
        M_set = set(list(M))
        assert inputs.issubset(M_set), \
            'Merged result is missing some problems'

    def test_name_change_unique(self):
        """
        Test that the names are unique after merging even when there is a clash
        """
        M, _ = merge_problems(self.A, self.C)
        M_set = set(list(M))
        assert len(M_set) == len(list(M)), \
            'Merged result contains repeated problems'

    def test_all_renamed_problems_listed(self):
        """
        Test that the list of problems that has been renamed is correct.
        """
        inputs = set(list(self.A)).union(set(list(self.B)))
        M, renamed = merge_problems(self.A, self.B)
        M_set = set(list(M))
        M_set_renamed = M_set - inputs
        assert sorted(M_set_renamed) == sorted(renamed), \
            'Listed renamed problems not the same as actual renamed problems'


class TestMergeResults(TestCase):
    """
    Test for the merge_results function
    """

    def setUp(self):
        """
        Generate 3 datasets (A, B, C) such that:
        - A and B and C have the same label
        - D has a unique label
        - A and B have 2 problems in common and 1 problem not in common
        - A and B have results for 2 softwares, only one of which is common
          between them
        - Problems in A and C have matching names but not matching data
        """
        ch_test_files = Path(__file__).parent / 'test_files'
        self.A = json.load((ch_test_files/'A.json').open()
                           )['DataSet1']['results']
        self.B = json.load((ch_test_files/'B.json').open()
                           )['DataSet1']['results']
        self.C = json.load((ch_test_files/'C.json').open()
                           )['DataSet1']['results']
        self.uid = lambda r: (r['name'],
                              r['software_tag'],
                              r['minimizer_tag'],
                              r['jacobian_tag'],
                              r['hessian_tag'],
                              r['costfun_tag'])

    def test_merged_results_subset_of_input(self):
        """
        Test that each result in the merged result is in at least one of the
        inputs.
        """
        A_ids = {self.uid(r) for r in self.A}
        B_ids = {self.uid(r) for r in self.B}
        inputs = A_ids.union(B_ids)
        M = merge_results(self.A, self.B)
        M_ids = {self.uid(r) for r in M}
        assert M_ids.issubset(inputs), \
            'Merged result contains extra results'

    def test_merged_results_superset_of_input(self):
        """
        Test that each result in the inputs is in the merged result.
        """
        A_ids = {self.uid(r) for r in self.A}
        B_ids = {self.uid(r) for r in self.B}
        inputs = A_ids.union(B_ids)
        M = merge_results(self.A, self.B)
        M_ids = {self.uid(r) for r in M}
        assert M_ids.issuperset(inputs), \
            'Merged results missing results'

    def test_no_duplicate_results(self):
        """
        Test that all of the results are unique runs.
        """
        M = merge_results(self.A, self.B)
        M_ids = {self.uid(r) for r in M}
        assert len(M) == len(M_ids), 'Merged results contain duplicates'

    def test_correct_result_taken(self):
        """
        Test that when results are identical, the correct one is taken.
        """
        M = merge_results(self.A, self.B)
        expected_r = None
        actual_r = None
        for r in self.A:
            if r['name'] == 'prob_0' and r['software'] == 'common1':
                expected_r = r
        for r in M:
            if r['name'] == 'prob_0' and r['software'] == 'common1':
                actual_r = r
        assert json.dumps(expected_r) == json.dumps(actual_r), \
            'Conflicting results merged incorrectly'
