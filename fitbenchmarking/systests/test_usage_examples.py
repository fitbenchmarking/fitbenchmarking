"""
Test that all usage examples from `fitbenchmarking --help``
run without errors
"""
from unittest import TestCase
from unittest import mock
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module
from conftest import run_for_test_types

from fitbenchmarking.cli import main


@run_for_test_types(TEST_TYPE, 'default')
class TestExamples(TestCase):
    """
    Test that all usage examples run as expected
    """
    @staticmethod
    def test_usage_examples():
        """
        Extract usage examples listed in `fitbenchmarking --help`
        and run each of them
        """
        # run get parser to get current usage examples
        parser = main.get_parser()
        # examples are listed in parser.epilog
        epilog_lines = parser.epilog.split('\n')

        examples = []
        for ln in epilog_lines:
            ln_strip = ln.strip()
            # all example lines start with "$"
            if ln_strip.startswith("$"):
                examples.append(ln_strip[ln_strip.index('f'):])

        # split string into list of arguments
        for example in examples:
            example_split = example.split(' ')
            args = []
            if len(example_split) > 1:
                options_indices = [example_split.index(x)
                                   for x in example_split
                                   if x in ['-o', '-p', '-d']]
                while len(options_indices) > 1:
                    args.append(' '.join(
                        example_split[options_indices[0]:options_indices[1]]))
                    options_indices = options_indices[1:]
                if options_indices[0] != len(example_split):
                    args.append(' '.join(example_split[options_indices[0]:]))

                for i, s in enumerate(example_split[:-1]):
                    if s in ['-o', '-p', '-d']:
                        args.append(
                            ''.join([example_split[i], example_split[i+1]]))
            else:
                args = example_split

            # mock sys.argv with args taken from usage example
            with mock.patch('sys.argv', args):
                main.main()
