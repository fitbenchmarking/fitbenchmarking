"""
Tests for renaming col tags if jacobian and hessian experience fallback
"""

import unittest

from fitbenchmarking.core.results_output import (_get_all_result_tags,
                                                 _find_non_full_columns,
                                                 _handle_fallback_tags,
                                                 preprocess_data)

from fitbenchmarking.core.tests.test_results_output import load_mock_results


class EdgeCaseTests(unittest.TestCase):
    """
    Unit tests for the edge cases.
    """
    def setUp(self):
        """
        Defining the edge case results
        """

        self.sort_order = (['problem'],
                           ['software',
                            'minimizer',
                            'jacobian',
                            'hessian'])
        self.col_sections = ['costfun']
        self.edgecases = [{
                'filename': 'edgecase1.json',
                'expected_tags': [{'row': 'cubic, Start 1',
                                   'col': 'ralfit:hybrid:'
                                          'scipy 2-point:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'cubic, Start 1',
                                   'col': 'ralfit:hybrid:'
                                          'numdifftools central:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit:hybrid:'
                                          'scipy 2-point:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit:hybrid:'
                                          'numdifftools central:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit:hybrid:'
                                          'scipy 2-point:',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit:hybrid:'
                                          'numdifftools central:',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5}],
                'expected_repeating_tags': ['ralfit:hybrid:'
                                            'scipy 2-point:analytic',
                                            'ralfit:hybrid:'
                                            'numdifftools central:analytic',
                                            'ralfit:hybrid:'
                                            'scipy 2-point:',
                                            'ralfit:hybrid:'
                                            'numdifftools central:'],
                'expected_new_tags': ['ralfit:hybrid:'
                                      'scipy 2-point:best_avaliable',
                                      'ralfit:hybrid:'
                                      'numdifftools central:best_avaliable',
                                      'ralfit:hybrid:'
                                      'scipy 2-point:best_avaliable',
                                      'ralfit:hybrid:'
                                      'numdifftools central:best_avaliable',
                                      'ralfit:hybrid:'
                                      'scipy 2-point:best_avaliable',
                                      'ralfit:hybrid:'
                                      'numdifftools central:best_avaliable']
            },
            {
                'filename': 'edgecase2.json',
                'expected_tags': [{'row': 'cubic, Start 1',
                                   'col': 'ralfit:hybrid:'
                                          'analytic:scipy 2-point',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'cubic, Start 1',
                                   'col': 'ralfit:hybrid:analytic:'
                                          'numdifftools central',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit:hybrid:'
                                          'analytic:scipy 2-point',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit:hybrid:'
                                          'analytic:numdifftools central',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit:hybrid:'
                                          'scipy 2-point:scipy 2-point',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit:hybrid:'
                                          'scipy 2-point:numdifftools central',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5}],
                'expected_repeating_tags': ['ralfit:hybrid:'
                                            'analytic:scipy 2-point',
                                            'ralfit:hybrid:'
                                            'analytic:numdifftools central',
                                            'ralfit:hybrid:'
                                            'scipy 2-point:scipy 2-point',
                                            'ralfit:hybrid:'
                                            'scipy 2-point:'
                                            'numdifftools central'],
                'expected_new_tags': ['ralfit:hybrid:'
                                      'best_avaliable:scipy 2-point',
                                      'ralfit:hybrid:'
                                      'best_avaliable:numdifftools central',
                                      'ralfit:hybrid:'
                                      'best_avaliable:scipy 2-point',
                                      'ralfit:hybrid:'
                                      'best_avaliable:numdifftools central',
                                      'ralfit:hybrid:'
                                      'best_avaliable:scipy 2-point',
                                      'ralfit:hybrid:'
                                      'best_avaliable:numdifftools central']
            },
            {
                'filename': 'edgecase3.json',
                'expected_tags': [{'row': 'cubic, Start 1',
                                   'col': 'ralfit:hybrid:analytic:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit:hybrid:analytic:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit:hybrid:scipy 2-point:',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'cubic, Start 1',
                                   'col': 'ralfit2:hybrid:analytic:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'cubic, Start 2',
                                   'col': 'ralfit2:hybrid:analytic:analytic',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'Problem Def 1',
                                   'col': 'ralfit2:hybrid:scipy 2-point:',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5}],
                'expected_repeating_tags': ['ralfit:hybrid:analytic:analytic',
                                            'ralfit:hybrid:scipy 2-point:',
                                            'ralfit2:hybrid:analytic:analytic',
                                            'ralfit2:hybrid:scipy 2-point:'],
                'expected_new_tags': ['ralfit:hybrid:'
                                      'best_avaliable:best_avaliable',
                                      'ralfit:hybrid:'
                                      'best_avaliable:best_avaliable',
                                      'ralfit:hybrid:'
                                      'best_avaliable:best_avaliable',
                                      'ralfit2:hybrid:'
                                      'best_avaliable:best_avaliable',
                                      'ralfit2:hybrid:'
                                      'best_avaliable:best_avaliable',
                                      'ralfit2:hybrid:'
                                      'best_avaliable:best_avaliable']
            },
            {
                'filename': 'edgecase4.json',
                'expected_tags': [{'row': 'p1',
                                   'col': 's1:m1:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'p2',
                                   'col': 's1:m1:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'p3',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'p4',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'p1',
                                   'col': 's1:m1:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'p2',
                                   'col': 's1:m1:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5},
                                  {'row': 'p3',
                                   'col': 's1:m1:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 6},
                                  {'row': 'p4',
                                   'col': 's1:m1:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 7}],
                'expected_repeating_tags': ['s1:m1:j1:h2',
                                            's1:m1:j1:h1',
                                            's1:m1:j2:h2',
                                            's1:m1:j2:h1'],
                'expected_new_tags': ['s1:m1:j1:best_avaliable',
                                      's1:m1:j1:best_avaliable',
                                      's1:m1:j1:best_avaliable',
                                      's1:m1:j1:best_avaliable',
                                      's1:m1:j2:best_avaliable',
                                      's1:m1:j2:best_avaliable',
                                      's1:m1:j2:best_avaliable',
                                      's1:m1:j2:best_avaliable']
            },
            {
                'filename': 'edgecase5.json',
                'expected_tags': [{'row': 'p1',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'p2',
                                   'col': 's1:m1:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'p3',
                                   'col': 's1:m1:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'p4',
                                   'col': 's1:m1:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'p5',
                                   'col': 's1:m1:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4}],
                'expected_repeating_tags': ['s1:m1:j1:h1',
                                            's1:m1:j1:h2',
                                            's1:m1:j2:h1',
                                            's1:m1:j2:h2'],
                'expected_new_tags': ['s1:m1:best_avaliable'
                                      ':best_avaliable',
                                      's1:m1:best_avaliable'
                                      ':best_avaliable',
                                      's1:m1:best_avaliable'
                                      ':best_avaliable',
                                      's1:m1:best_avaliable'
                                      ':best_avaliable',
                                      's1:m1:best_avaliable'
                                      ':best_avaliable']
            },
            {
                'filename': 'edgecase6.json',
                'expected_tags': [{'row': 'p1',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'p2',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'p3',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'p4',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'p1',
                                   'col': 's1:m2:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'p2',
                                   'col': 's1:m2:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5},
                                  {'row': 'p3',
                                   'col': 's1:m2:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 6},
                                  {'row': 'p4',
                                   'col': 's1:m2:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 7},
                                  {'row': 'p1',
                                   'col': 's1:m3:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 8},
                                  {'row': 'p2',
                                   'col': 's1:m3:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 9},
                                  {'row': 'p3',
                                   'col': 's1:m3:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 10},
                                  {'row': 'p4',
                                   'col': 's1:m3:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 11},
                                  {'row': 'p1',
                                   'col': 's1:m4:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 12},
                                  {'row': 'p2',
                                   'col': 's1:m4:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 13},
                                  {'row': 'p3',
                                   'col': 's1:m4:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 14},
                                  {'row': 'p4',
                                   'col': 's1:m4:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 15},
                                  {'row': 'p1',
                                   'col': 's1:m5:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 16},
                                  {'row': 'p2',
                                   'col': 's1:m5:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 17},
                                  {'row': 'p3',
                                   'col': 's1:m5:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 18},
                                  {'row': 'p4',
                                   'col': 's1:m5:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 19},
                                  {'row': 'p1',
                                   'col': 's1:m6:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 20},
                                  {'row': 'p2',
                                   'col': 's1:m6:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 21},
                                  {'row': 'p3',
                                   'col': 's1:m6:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 22},
                                  {'row': 'p4',
                                   'col': 's1:m6:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 23},
                                  {'row': 'p1',
                                   'col': 's1:m7:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 24},
                                  {'row': 'p2',
                                   'col': 's1:m7:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 25},
                                  {'row': 'p3',
                                   'col': 's1:m7:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 26},
                                  {'row': 'p4',
                                   'col': 's1:m7:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 27}],
                'expected_repeating_tags': ['s1:m2:j1:h1',
                                            's1:m2:j1:h2',
                                            's1:m3:j1:h1',
                                            's1:m3:j2:h1',
                                            's1:m4:j1:h1',
                                            's1:m4:j2:h2',
                                            's1:m5:j1:h1',
                                            's1:m5:j1:h2',
                                            's1:m5:j2:h1',
                                            's1:m5:j2:h2',
                                            's1:m6:j1:h1',
                                            's1:m6:j1:h2',
                                            's1:m6:j2:h2',
                                            's1:m7:j1:h1',
                                            's1:m7:j2:h1',
                                            's1:m7:j2:h2'],
                'expected_new_tags': ['s1:m1:j1:h1',
                                      's1:m1:j1:h1',
                                      's1:m1:j1:h1',
                                      's1:m1:j1:h1',
                                      's1:m2:j1:best_avaliable',
                                      's1:m2:j1:best_avaliable',
                                      's1:m2:j1:best_avaliable',
                                      's1:m2:j1:best_avaliable',
                                      's1:m3:best_avaliable:h1',
                                      's1:m3:best_avaliable:h1',
                                      's1:m3:best_avaliable:h1',
                                      's1:m3:best_avaliable:h1',
                                      's1:m4:best_avaliable:best_avaliable',
                                      's1:m4:best_avaliable:best_avaliable',
                                      's1:m4:best_avaliable:best_avaliable',
                                      's1:m4:best_avaliable:best_avaliable',
                                      's1:m5:best_avaliable:best_avaliable',
                                      's1:m5:best_avaliable:best_avaliable',
                                      's1:m5:best_avaliable:best_avaliable',
                                      's1:m5:best_avaliable:best_avaliable',
                                      's1:m6:best_avaliable:best_avaliable',
                                      's1:m6:best_avaliable:best_avaliable',
                                      's1:m6:best_avaliable:best_avaliable',
                                      's1:m6:best_avaliable:best_avaliable',
                                      's1:m7:best_avaliable:best_avaliable',
                                      's1:m7:best_avaliable:best_avaliable',
                                      's1:m7:best_avaliable:best_avaliable',
                                      's1:m7:best_avaliable:best_avaliable']
            }]

    def test_edge_cases(self):
        """
        Test each of the edgecases
        """
        for edgecase in self.edgecases:

            with self.subTest(edgecase['filename']):

                results, _ = load_mock_results(filename=edgecase['filename'])

                actual_tags, actual_repeating_tags = \
                    _get_all_result_tags(results,
                                         self.sort_order,
                                         self.col_sections)

                self.assertEqual(actual_tags, edgecase['expected_tags'])
                self.assertEqual(actual_repeating_tags,
                                 edgecase['expected_repeating_tags'])

                actual_results, actual_result_tags = \
                    _handle_fallback_tags(results,
                                          actual_tags,
                                          actual_repeating_tags,
                                          self.sort_order[1])

                actual_new_tags = [tag['col'] for tag in actual_result_tags]
                self.assertEqual(actual_results, results)
                self.assertEqual(actual_new_tags,
                                 edgecase['expected_new_tags'])

                _, sorted_results = preprocess_data(results)

                all_sorted_results = [result for row in
                                      sorted_results.values()
                                      for result in row.values()]
                for r in all_sorted_results:
                    self.assertNotIn(None, r)


class FallbackTagTests(unittest.TestCase):
    """
    Unit tests for finding fallback tags that
    occur when there is a fallback on jacobian
    and hessians.
    """
    def setUp(self):
        """
        Setting up the test results
        """
        # Loading the results from checkpoint.json
        self.results, _ = load_mock_results()

        self.sort_order = (['problem'],
                           ['software',
                            'minimizer',
                            'jacobian',
                            'hessian'])
        self.col_sections = ['costfun']

        # Defining the expected values for results in checkpoint.json
        self.expected_tags = [{'row': 'prob_0', 'col': 's1:m10:j0:',
                               'cat': 'cf1', 'result_ix': 0},
                              {'row': 'prob_0', 'col': 's1:m11:j0:',
                               'cat': 'cf1', 'result_ix': 1},
                              {'row': 'prob_0', 'col': 's0:m01:j0:',
                               'cat': 'cf1', 'result_ix': 2},
                              {'row': 'prob_0', 'col': 's1:m10:j1:',
                               'cat': 'cf1', 'result_ix': 4},
                              {'row': 'prob_0', 'col': 's1:m11:j1:',
                               'cat': 'cf1', 'result_ix': 5},
                              {'row': 'prob_0', 'col': 's0:m01:j1:',
                               'cat': 'cf1', 'result_ix': 6},
                              {'row': 'prob_1', 'col': 's1:m10:j0:',
                               'cat': 'cf1', 'result_ix': 7},
                              {'row': 'prob_1', 'col': 's1:m11:j0:',
                               'cat': 'cf1', 'result_ix': 8},
                              {'row': 'prob_1', 'col': 's0:m01:j0:',
                               'cat': 'cf1', 'result_ix': 9},
                              {'row': 'prob_1', 'col': 's0:m00:j0:',
                               'cat': 'cf1', 'result_ix': 10},
                              {'row': 'prob_1', 'col': 's1:m10:j1:',
                               'cat': 'cf1', 'result_ix': 11},
                              {'row': 'prob_1', 'col': 's1:m11:j1:',
                               'cat': 'cf1', 'result_ix': 12},
                              {'row': 'prob_1', 'col': 's0:m01:j1:',
                               'cat': 'cf1', 'result_ix': 13},
                              {'row': 'prob_1', 'col': 's0:m00:j1:',
                               'cat': 'cf1', 'result_ix': 14}]
        self.expected_repeating_tags = []

    def test_get_all_result_tags(self):
        """
        Test the _get_all_result_tags function
        """
        results = self.results
        expected_tags = self.expected_tags
        expected_repeating_tags = self.expected_repeating_tags

        actual_tags, actual_repeating_tags = \
            _get_all_result_tags(results,
                                 self.sort_order,
                                 self.col_sections)

        self.assertEqual(actual_tags, expected_tags)
        self.assertEqual(actual_repeating_tags, expected_repeating_tags)

    def run_and_match_find_non_full_columns(self,
                                            columns,
                                            expected_count,
                                            columns_with_errors,
                                            expected_column_tags):
        """
        Helper function to call _find_non_full_columns
        and match outputs
        """
        actual_column_tags = _find_non_full_columns(columns,
                                                    expected_count,
                                                    columns_with_errors)
        self.assertEqual(actual_column_tags, expected_column_tags)

    def test_find_non_full_columns(self):
        """
        Test the _find_non_full_columns function
        """
        columns = {'s1:m10:j0:': 2,
                   's1:m11:j0:': 2,
                   's0:m01:j0:': 2,
                   's1:m10:j1:': 2,
                   's1:m11:j1:': 2,
                   's0:m01:j1:': 2,
                   's0:m00:j0:': 1,
                   's0:m00:j1:': 1}
        expected_count = 2
        columns_with_errors = {'s0:m00:[^:]*:[^:]*': 1}

        # Test Case 1
        # Using the results in checkpoint.json
        # No column with fallback
        # 1 Error result
        expected_column_tags = []
        self.run_and_match_find_non_full_columns(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 2
        # Using the results in checkpoint.json
        # 1 column with fallback
        # 0 Error result
        columns_with_errors = {}
        columns['s0:m00:j0:'] = columns['s0:m00:j1:'] = 2
        expected_column_tags = []
        self.run_and_match_find_non_full_columns(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 3
        # Using the results in checkpoint.json
        # 2 column with fallback
        # 0 Error result
        columns['s1:m11:j0:'] = columns['s1:m11:j1:'] = 1
        expected_column_tags = ['s1:m11:j0:', 's1:m11:j1:']
        self.run_and_match_find_non_full_columns(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

        # Test Case 4
        # Using the results in checkpoint.json
        # 2 column with fallback
        # 0 Error result
        columns['s1:m11:j0:h0'] = columns['s1:m11:j1:h1'] = 1
        expected_column_tags = ['s1:m11:j0:',
                                's1:m11:j1:',
                                's1:m11:j0:h0',
                                's1:m11:j1:h1']
        self.run_and_match_find_non_full_columns(columns,
                                                 expected_count,
                                                 columns_with_errors,
                                                 expected_column_tags)

    def test_handle_fallback_tags(self):
        """
        Test the handle fallback tags function
        """
        results = self.results
        expected_tags = self.expected_tags
        repeating_tags = []

        actual_results, actual_result_tags = \
            _handle_fallback_tags(results,
                                  expected_tags,
                                  repeating_tags,
                                  self.sort_order[1])

        self.assertEqual(actual_results, results)
        self.assertEqual(actual_result_tags, expected_tags)
