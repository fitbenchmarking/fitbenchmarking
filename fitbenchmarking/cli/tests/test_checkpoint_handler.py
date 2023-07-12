"""
Tests for checkpoint_handler.py
"""
import inspect
import pathlib
from tempfile import TemporaryDirectory
from unittest import TestCase

from fitbenchmarking import test_files
from fitbenchmarking.cli.checkpoint_handler import generate_report


class TestCheckpointHandler(TestCase):
    """
    Simple testing for the checkpoint_handler entry point
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
        cp_dir = pathlib.Path(inspect.getfile(test_files)).parent
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
            'Fake_Test_Data/support_pages/figures/start_for_prob_0.html',
        ]

        with TemporaryDirectory() as results_dir:
            results = pathlib.Path(results_dir)
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
