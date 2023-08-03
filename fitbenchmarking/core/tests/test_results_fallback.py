"""
Tests for renaming col tags if jacobian and hessian experience fallback
"""

import unittest

from fitbenchmarking.core.results_output import (_get_all_result_tags,
                                                 _find_non_full_columns,
                                                 _find_tag_to_rename,
                                                 _handle_fallback_tags)

from fitbenchmarking.core.tests.test_results_output import load_mock_results


class RenameFallbackColumnTagTests(unittest.TestCase):
    """
    Unit tests for the functions handling renaming
    jacobian and hessian tags in various fallback
    scenarios.
    """

    def setUp(self):
        """
        Defining the fallback cases results

        Case 1: filename : 'fallbackcase1.json'
        Case 2: filename : 'fallbackcase2.json'
        Case 3: filename : 'fallbackcase3.json'
        Case 4: filename : 'fallbackcase4.json'
        Case 5: filename : 'fallbackcase5.json'
        Case 6: filename : 'fallbackcase6.json'
        Case 7: filename : 'fallbackcase7.json'
        Case 8: filename : 'checkpoint.json'
        """

        self.sort_order = (['problem'],
                           ['software',
                            'minimizer',
                            'jacobian',
                            'hessian'])
        self.col_sections = ['costfun']
        self.fallbackcases = [{
                'filename': 'fallbackcase1.json',
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
                                      'numdifftools central:best_avaliable'],
                'columns': {'ralfit:hybrid:scipy 2-point:analytic': 2,
                            'ralfit:hybrid:numdifftools central:analytic': 2,
                            'ralfit:hybrid:scipy 2-point:': 1,
                            'ralfit:hybrid:numdifftools central:': 1},
                'expected_count': 3,
                'columns_with_errors': {},
                'sm_summary': {('ralfit', 'hybrid'): {'ralfit:hybrid:'
                                                      'scipy 2-point:analytic',
                                                      'ralfit:hybrid'
                                                      ':scipy 2-point:',
                                                      'ralfit:hybrid:'
                                                      'numdifftools central'
                                                      ':analytic',
                                                      'ralfit:hybrid:'
                                                      'numdifftools '
                                                      'central:'}},
                'expected_update_summary': {('ralfit', 'hybrid'): 'hessian'}
            },
            {
                'filename': 'fallbackcase2.json',
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
                                      'best_avaliable:numdifftools central'],
                'sm_summary': {('ralfit', 'hybrid'): {'ralfit:hybrid:'
                                                      'analytic:'
                                                      'numdifftools central',
                                                      'ralfit:hybrid:'
                                                      'analytic:scipy 2-point',
                                                      'ralfit:hybrid:'
                                                      'scipy 2-point:'
                                                      'numdifftools central',
                                                      'ralfit:hybrid:'
                                                      'scipy 2-point:'
                                                      'scipy 2-point'}},
                'expected_update_summary': {('ralfit', 'hybrid'): 'jacobian'}
            },
            {
                'filename': 'fallbackcase3.json',
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
                                      'best_avaliable:best_avaliable'],
                'sm_summary': {('ralfit', 'hybrid'): {'ralfit:hybrid'
                                                      ':scipy 2-point:',
                                                      'ralfit:hybrid:'
                                                      'analytic:analytic'},
                               ('ralfit2', 'hybrid'): {'ralfit2:hybrid:'
                                                       'scipy 2-point:',
                                                       'ralfit2:hybrid:'
                                                       'analytic:analytic'}},
                'expected_update_summary': {('ralfit', 'hybrid'): 'both',
                                            ('ralfit2', 'hybrid'): 'both'}
            },
            {
                'filename': 'fallbackcase4.json',
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
                                      's1:m1:j2:best_avaliable'],
                'sm_summary': {('s1', 'm1'): {'s1:m1:j1:h1',
                                              's1:m1:j2:h1',
                                              's1:m1:j1:h2',
                                              's1:m1:j2:h2'}},
                'expected_update_summary': {('s1', 'm1'): 'hessian'}
            },
            {
                'filename': 'fallbackcase5.json',
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
                                      ':best_avaliable'],
                'sm_summary': {('s1', 'm1'): {'s1:m1:j2:h1',
                                              's1:m1:j2:h2',
                                              's1:m1:j1:h2',
                                              's1:m1:j1:h1'}},
                'expected_update_summary': {('s1', 'm1'): 'both'}
            },
            {
                'filename': 'fallbackcase6.json',
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
                                      's1:m7:best_avaliable:best_avaliable'],
                'columns': {'s1:m1:j1:h1': 4,
                            's1:m2:j1:h1': 3,
                            's1:m2:j1:h2': 1,
                            's1:m3:j1:h1': 2,
                            's1:m3:j2:h1': 2,
                            's1:m4:j1:h1': 2,
                            's1:m4:j2:h2': 2,
                            's1:m5:j1:h1': 1,
                            's1:m5:j1:h2': 1,
                            's1:m5:j2:h1': 1,
                            's1:m5:j2:h2': 1,
                            's1:m6:j1:h1': 2,
                            's1:m6:j1:h2': 1,
                            's1:m6:j2:h2': 1,
                            's1:m7:j1:h1': 2,
                            's1:m7:j2:h1': 1,
                            's1:m7:j2:h2': 1},
                'expected_count': 4,
                'columns_with_errors': {},
                'sm_summary': {('s1', 'm1'): {'s1:m1:j1:h1'},
                               ('s1', 'm2'): {'s1:m2:j1:h1',
                                              's1:m2:j1:h2'},
                               ('s1', 'm3'): {'s1:m3:j2:h1',
                                              's1:m3:j1:h1'},
                               ('s1', 'm4'): {'s1:m4:j1:h1',
                                              's1:m4:j2:h2'},
                               ('s1', 'm5'): {'s1:m5:j1:h1',
                                              's1:m5:j2:h1',
                                              's1:m5:j1:h2',
                                              's1:m5:j2:h2'},
                               ('s1', 'm6'): {'s1:m6:j1:h1',
                                              's1:m6:j2:h2',
                                              's1:m6:j1:h2'},
                               ('s1', 'm7'): {'s1:m7:j2:h2',
                                              's1:m7:j2:h1',
                                              's1:m7:j1:h1'}},
                'expected_update_summary': {('s1', 'm2'): 'hessian',
                                            ('s1', 'm3'): 'jacobian',
                                            ('s1', 'm4'): 'both',
                                            ('s1', 'm5'): 'both',
                                            ('s1', 'm6'): 'both',
                                            ('s1', 'm7'): 'both'}
            },
            {
                'filename': 'fallbackcase7.json',
                'expected_tags': [{'row': 'p1',
                                   'col': 's1:m1:j1:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 0},
                                  {'row': 'p2',
                                   'col': 's1:m1:j1:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 1},
                                  {'row': 'p1',
                                   'col': 's1:m1:j2:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 2},
                                  {'row': 'p2',
                                   'col': 's1:m1:j2:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 3},
                                  {'row': 'p1',
                                   'col': 's1:m1:j3:h1',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 4},
                                  {'row': 'p2',
                                   'col': 's1:m1:j3:h2',
                                   'cat': 'WeightedNLLSCostFunc',
                                   'result_ix': 5}],
                'expected_repeating_tags': ['s1:m1:j1:h1',
                                            's1:m1:j1:h2',
                                            's1:m1:j2:h1',
                                            's1:m1:j2:h2',
                                            's1:m1:j3:h1',
                                            's1:m1:j3:h2'],
                'expected_new_tags': ['s1:m1:j1:best_avaliable',
                                      's1:m1:j1:best_avaliable',
                                      's1:m1:j2:best_avaliable',
                                      's1:m1:j2:best_avaliable',
                                      's1:m1:j3:best_avaliable',
                                      's1:m1:j3:best_avaliable'],
                'columns': {'s1:m1:j1:h1': 1,
                            's1:m1:j1:h2': 1,
                            's1:m1:j2:h1': 1,
                            's1:m1:j2:h2': 1,
                            's1:m1:j3:h1': 1,
                            's1:m1:j3:h2': 1},
                'expected_count': 2,
                'columns_with_errors': {},
                'sm_summary': {('s1', 'm1'): {'s1:m1:j1:h1',
                                              's1:m1:j2:h2',
                                              's1:m1:j3:h1',
                                              's1:m1:j3:h2',
                                              's1:m1:j2:h1',
                                              's1:m1:j1:h2'}},
                'expected_update_summary': {('s1', 'm1'): 'hessian'}
            },
            {
                'filename': 'checkpoint.json',
                'expected_tags': [{'row': 'prob_0',
                                   'col': 's1:m10:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 0},
                                  {'row': 'prob_0',
                                   'col': 's1:m11:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 1},
                                  {'row': 'prob_0',
                                   'col': 's0:m01:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 2},
                                  {'row': 'prob_0',
                                   'col': 's1:m10:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 4},
                                  {'row': 'prob_0',
                                   'col': 's1:m11:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 5},
                                  {'row': 'prob_0',
                                   'col': 's0:m01:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 6},
                                  {'row': 'prob_1',
                                   'col': 's1:m10:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 7},
                                  {'row': 'prob_1',
                                   'col': 's1:m11:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 8},
                                  {'row': 'prob_1',
                                   'col': 's0:m01:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 9},
                                  {'row': 'prob_1',
                                   'col': 's0:m00:j0:',
                                   'cat': 'cf1',
                                   'result_ix': 10},
                                  {'row': 'prob_1',
                                   'col': 's1:m10:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 11},
                                  {'row': 'prob_1',
                                   'col': 's1:m11:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 12},
                                  {'row': 'prob_1',
                                   'col': 's0:m01:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 13},
                                  {'row': 'prob_1',
                                   'col': 's0:m00:j1:',
                                   'cat': 'cf1',
                                   'result_ix': 14}],
                'expected_repeating_tags': [],
                'columns': {'s1:m10:j0:': 2,
                            's1:m11:j0:': 2,
                            's0:m01:j0:': 2,
                            's1:m10:j1:': 2,
                            's1:m11:j1:': 2,
                            's0:m01:j1:': 2,
                            's0:m00:j0:': 1,
                            's0:m00:j1:': 1},
                'expected_count': 2,
                'columns_with_errors': {'s0:m00:[^:]*:[^:]*': 1}
            }]

    def test_find_non_full_columns(self):
        """
        Unit tests for _find_non_full_columns().

        Case 1: 4 non full columns.

        Case 2: 16 non full columns.

        Case 3: 6 non full columns.

        Case 4: 2 non full columns.
                One error_flag = 4
        """
        testcases_to_run = [e for e in self.fallbackcases
                            if e['filename'] in ['fallbackcase1.json',
                                                 'fallbackcase6.json',
                                                 'fallbackcase7.json',
                                                 'checkpoint.json']]

        for case in testcases_to_run:

            with self.subTest(case['filename']):

                actual_repeating_tags = \
                    _find_non_full_columns(case['columns'],
                                           case['expected_count'],
                                           case['columns_with_errors'])
                self.assertEqual(actual_repeating_tags,
                                 case['expected_repeating_tags'])

    def test_get_all_result_tags(self):
        """
        Unit tests for _get_all_result_tags().

        Case 1: Columns with only HESSIAN fallbacks
                4 repeating tags, len(results) = 6
                expected sorted_result table 3x2

        Case 2: Columns with only JACOBIAN fallbacks
                4 repeating tags, len(results) = 6
                expected sorted_result table 3x2

        Case 3: Columns with only BOTH fallbacks
                4 repeating tags, len(results) = 6
                expected sorted_result table 3x2

        Case 4: Columns with only HESSIAN fallbacks
                4 repeating tags, len(results) = 8
                expected sorted_result table 4x2

        Case 5: Columns with only BOTH fallbacks
                4 repeating tags, len(results) = 5
                expected sorted_result table 5x1

        Case 6: Columns with JACOBIAN, HESSIAN and BOTH
                fallbacks simultaneously
                16 repeating tags, len(results) = 28
                expected sorted_result table 4x7

        Case 7: Columns with only HESSIAN fallbacks
                6 repeating tags, len(results) = 6
                expected sorted_result table 2x3

        Case 8: Columns with NO fallbacks
                0 repeating tags, len(results) = 15
                expected sorted_result table 2x8
        """
        for case in self.fallbackcases:

            with self.subTest(case['filename']):

                results, _ = load_mock_results(filename=case['filename'])

                actual_tags, actual_repeating_tags = \
                    _get_all_result_tags(results,
                                         self.sort_order,
                                         self.col_sections)

                self.assertEqual(actual_tags, case['expected_tags'])
                self.assertEqual(actual_repeating_tags,
                                 case['expected_repeating_tags'])

    def test_handle_fallback_tags(self):
        """
        Unit tests for _handle_fallback_tags().

        Case 1: Rename HESSIAN tags
                expected sorted_result table 3x2

        Case 2: Rename JACOBIAN tags
                expected sorted_result table 3x2

        Case 3: Rename BOTH tags
                expected sorted_result table 3x2

        Case 4: Rename HESSIAN tags
                expected sorted_result table 4x2

        Case 5: Rename BOTH tags
                expected sorted_result table 5x1

        Case 6: Rename JACOBIAN, HESSIAN and BOTH
                tags simultaneously
                expected sorted_result table 4x7

        Case 7: Rename HESSIAN tags
                expected sorted_result table 2x3
        """
        for case in [e for e in self.fallbackcases
                     if e['filename'] != 'checkpoint.json']:

            with self.subTest(case['filename']):

                results, _ = load_mock_results(filename=case['filename'])

                actual_results, actual_result_tags = \
                    _handle_fallback_tags(results,
                                          case['expected_tags'],
                                          case['expected_repeating_tags'],
                                          self.sort_order[1])

                actual_new_tags = [tag['col'] for tag in actual_result_tags]
                self.assertEqual(actual_results, results)
                self.assertEqual(actual_new_tags,
                                 case['expected_new_tags'])

    def test_find_tag_to_rename(self):
        """
        Unit tests for _find_tag_to_rename().

        Case 1: Columns with only HESSIAN fallbacks
                1 column to be renamed
                expected sorted_result table 3x2

        Case 2: Columns with only JACOBIAN fallbacks
                1 column to be renamed
                expected sorted_result table 3x2

        Case 3: Columns with only BOTH fallbacks
                2 column to be renamed
                expected sorted_result table 3x2

        Case 4: Columns with only HESSIAN fallbacks
                1 column to be renamed
                expected sorted_result table 4x2

        Case 5: Columns with only BOTH fallbacks
                1 column to be renamed
                expected sorted_result table 5x1

        Case 6: Columns with JACOBIAN, HESSIAN and BOTH
                fallbacks simultaneously
                6 column to be renamed
                expected sorted_result table 4x7

        Case 7: Columns with only HESSIAN fallbacks
                1 column to be renamed
                expected sorted_result table 2x3

        """
        for case in [e for e in self.fallbackcases
                     if e['filename'] != 'checkpoint.json']:

            with self.subTest(case['filename']):

                actual_update_summary = \
                    _find_tag_to_rename(case['expected_tags'],
                                        case['sm_summary'],
                                        self.sort_order[1],
                                        case['expected_repeating_tags'])

                self.assertEqual(actual_update_summary,
                                 case['expected_update_summary'])
