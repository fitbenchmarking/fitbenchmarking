from __future__ import (absolute_import, division, print_function)

import unittest
import os

# Delete four lines below when automated tests ar enabled
import sys
test_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.normpath(test_dir))
main_dir = os.path.dirname(os.path.normpath(parent_dir))
sys.path.insert(0, main_dir)

from utils import fitbm_result
from utils import fitbm_problem
from resproc.misc import display_name_for_minimizers
from resproc.misc import weighted_suffix_string
from resproc.misc import build_items_links


class MiscTests(unittest.TestCase):

  def test_displayNameForMinimizers_return_minimizer_mock_names(self):

    names = ['Minimizer1', 'Minimizer2', 'Minimizer3', 'Minimizer4',
             'Minimizer5', 'Minimizer6', 'Minimizer7', 'Minimizer8',
             'Minimizer9', 'DTRS']

    display_names = display_name_for_minimizers(names)
    display_names_expected = ['Minimizer1', 'Minimizer2', 'Minimizer3',
                              'Minimizer4', 'Minimizer5',
                              'Minimizer6', 'Minimizer7', 'Minimizer8',
                              'Minimizer9', 'Trust Region']

    self.assertListEqual(display_names_expected, display_names)

  def test_weightedSuffixString_return_string_value_weighted(self):

    value = weighted_suffix_string(True)
    self.assertEqual(value, 'weighted')

  def test_weightedSuffixString_return_string_value_unweighted(self):

    value = weighted_suffix_string(False)
    self.assertEqual(value, 'unweighted')

  def test_buildItemsLinks_return_summary_links(self):

    comparison_type = 'summary'
    comparison_dim = 'accuracy'
    using_errors = True

    items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
    items_link_expected = ['Minimizers_weighted_comparison_in_terms_of'
                           '_accuracy_nist_lower',
                           'Minimizers_weighted_comparison_in_terms_of'
                           '_accuracy_nist_average',
                           'Minimizers_weighted_comparison_in_terms_of'
                           '_accuracy_nist_higher',
                           'Minimizers_weighted_comparison_in_terms_of'
                           '_accuracy_cutest',
                           'Minimizers_weighted_comparison_in_terms_of'
                           '_accuracy_neutron_data']

    self.assertListEqual(items_link_expected, items_link)

  def test_buildItemsLinks_return_accuracy_links(self):

    comparison_type = 'accuracy'
    comparison_dim = ''
    using_errors = True

    items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
    items_link_expected = 'FittingMinimizersComparisonDetailedWithWeights'

    self.assertEqual(items_link_expected, items_link)

  def test_buildItemsLinks_return_runtime_links(self):

    comparison_type = 'runtime'
    comparison_dim = ''
    using_errors = False

    items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
    items_link_expected = 'FittingMinimizersComparisonDetailed'

    self.assertEqual(items_link_expected, items_link)

  def test_buildItemsLinks_return_empty_itemsLinks_invalid_comparison(self):

    comparison_type = 'pasta'
    comparison_dim = ''
    using_errors = False

    items_link = \
        build_items_links(comparison_type, comparison_dim, using_errors)
    items_link_expected = ''

    self.assertEqual(items_link_expected, items_link)


if __name__ == "__main__":
  unittest.main()
