from __future__ import (absolute_import, division, print_function)
import inspect
import os
import shutil
import time
import unittest

from fitbenchmarking import mock_problems
from fitbenchmarking.utils.misc import get_problem_files
from fitbenchmarking.utils.misc import get_css, get_js
from fitbenchmarking.utils.options import Options

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

    def test_get_css(self):
        
        options = Options()
        print(options.results_dir)
        test_dir = os.path.join(options.results_dir,"foo")
        
        expected_css_dir = os.path.join("..","css")
        expected_main_css = os.path.join(expected_css_dir,"main_style.css")
        expected_table_css = os.path.join(expected_css_dir,"table_style.css")
        expected_custom_css = os.path.join(expected_css_dir,"custom_style.css")
        css = get_css(options,test_dir)

        self.assertEqual(css['main'], expected_main_css)
        self.assertEqual(css['table'], expected_table_css)
        self.assertEqual(css['custom'], expected_custom_css)

    def test_get_js(self):
        
        options = Options()
        print(options.results_dir)
        test_dir = os.path.join(options.results_dir,"foo")
        
        expected_js_dir = os.path.join("..","js")
        expected_mathjax_js = os.path.join(expected_js_dir,"tex-mml-chtml.js")
        js = get_js(options,test_dir)

        self.assertEqual(js['mathjax'], expected_mathjax_js)

if __name__ == "__main__":
    unittest.main()
