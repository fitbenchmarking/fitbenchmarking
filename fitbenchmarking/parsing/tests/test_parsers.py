"""
This file contains tests for the parsers.
"""

from importlib import import_module
from inspect import isclass, isabstract, getmembers
from json import load
import numpy as np
import os

from fitbenchmarking.parsing.base_parser import Parser
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.parsing.parser_factory import ParserFactory


def pytest_generate_tests(metafunc):
    """
    Function used by pytest to parametrize tests.
    This will create a set of tests for each function in the class where
    the parameters are given in a 'params' dict in the class.
    """
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    argvals = [[funcargs[name]
                for name in argnames]
               for funcargs in funcarglist]
    metafunc.parametrize(argnames,
                         argvals)


def generate_test_cases():
    """
    Utility function to create the params dict for parametrising the tests.

    :return: params dictionary with a function name as a key, and a list of
             parameter dictionaries for the value
    :rtype: dict
    """
    params = {'test_parsers': [],
              'test_factory': [],
              'test_function_evaluation': []}

    # get all parsers
    test_dir = os.path.dirname(__file__)
    formats = [f[:-10] for f in os.listdir(os.path.join(test_dir, os.pardir))
               if f.endswith('_parser.py')
               and f != 'base_parser.py']
    for known_format in ['nist', 'fitbenchmark', 'sasview']:
        if known_format not in formats:
            raise RuntimeError(
                'Could not find parser for {}'.format(known_format))

    # create list of test_cases
    expected_dir = os.listdir(os.path.join(test_dir, 'expected'))
    for file_format in formats:
        format_dir = os.listdir(os.path.join(test_dir, file_format))
        for expected_file in expected_dir:
            expected_path = os.path.join(test_dir, 'expected', expected_file)
            test_name = os.path.splitext(expected_file)[0]
            test_name_with_ext = [f for f in format_dir
                                  if f.startswith(test_name)]
            if not test_name_with_ext:
                test_file = None
            elif len(test_name_with_ext) == 1:
                test_file = os.path.join(test_dir,
                                         file_format,
                                         test_name_with_ext[0])
            else:
                raise RuntimeError(
                    'Too many "{}" files found for "{}" test'.format(
                        file_format, test_name))

            test_parsers = {}
            test_parsers['file_format'] = file_format
            test_parsers['test_file'] = test_file
            test_parsers['expected'] = load_expectation(expected_path)
            params['test_parsers'].append(test_parsers)

            test_factory = {}
            test_factory['file_format'] = file_format
            test_factory['test_file'] = test_file
            params['test_factory'].append(test_factory)

        func_eval = os.path.join(test_dir,
                                 file_format,
                                 'function_evaluations.json')
        test_func_eval = {}
        test_func_eval['file_format'] = file_format
        test_func_eval['evaluations_file'] = func_eval
        params['test_function_evaluation'].append(test_func_eval)

    return params


def load_expectation(filename):
    """
    Load an expected fitting problem from a json file.

    :param filename: The path to the expectation file
    :type filename: string
    :return: A fitting problem to test against
    :rtype: fitbenchmarking.parsing.FittingProblem
    """
    with open(filename, 'r') as f:
        expectation_dict = load(f)

    expectation = FittingProblem()
    expectation.name = expectation_dict['name']
    expectation.start_x = expectation_dict['start_x']
    expectation.end_x = expectation_dict['end_x']
    expectation.data_x = np.array(expectation_dict['data_x'])
    expectation.data_y = np.array(expectation_dict['data_y'])
    expectation.data_e = expectation_dict['data_e']
    if expectation.data_e is not None:
        expectation.data_e = np.array(expectation.data_e)
    expectation.functions = expectation_dict['functions']
    expectation.starting_values = expectation_dict['starting_values']
    expectation.value_ranges = expectation_dict['value_ranges']

    return expectation


class TestParsers:
    """
    A class to hold the tests for parametrized testing of parsers.
    """

    params = generate_test_cases()

    def test_parsers(self, file_format, test_file, expected):
        """
        Test that the parser correctly parses the specified input file.

        :param file_format: The name of the file format
        :type file_format: string
        :param test_file: The path to the test file
        :type test_file: string
        """
        assert (test_file is not None), \
            'No test file for {}'.format(file_format)

        # Test import
        module = import_module(name='.{}_parser'.format(file_format),
                               package='fitbenchmarking.parsing')

        parser = getmembers(module, lambda m: (isclass(m)
                                               and not isabstract(m)
                                               and issubclass(m, Parser)
                                               and m is not Parser))[0][1]

        # Test parse
        with parser(test_file) as p:
            fitting_problem = p.parse()

        # Allow for problems not supporting certain test cases
        # (e.g. value_ranges)
        if fitting_problem.name == 'NA':
            return

        # Check against expected
        fitting_problem.verify()

        # functions and equation need to be done seperately as they can't be
        # generic across problem types.
        # similarly starting_values uses the param name so must be checked
        # separately
        for attr in ['name', 'data_x', 'data_y', 'data_e', 'start_x', 'end_x',
                     'value_ranges']:
            parsed_attr = getattr(fitting_problem, attr)
            expected_attr = getattr(expected, attr)
            equal = (parsed_attr == expected_attr)
            if isinstance(equal, np.ndarray):
                equal = equal.all()
            assert (equal), '{} was parsed incorrectly.'.format(attr) \
                + '{} != {}'.format(parsed_attr, expected_attr)

        # Check starting_values, but ignore the param names
        for a, e in zip(fitting_problem.starting_values,
                        expected.starting_values):
            assert (a[1] == e[1]), 'starting_values were parsed incorrectly.'

        # Check functions length but nothing else here.
        assert (len(fitting_problem.functions) == len(expected.functions)), \
            'functions were parsed incorrectly.'

    def test_function_evaluation(self, file_format, evaluations_file):
        """
        Tests that the function evaluation is consistent with what would be
        expected by comparing to some precomputed values with fixed params and
        x values.

        :param file_format: The name of the file format
        :type file_format: string
        :param evaluations_file: Path to a json file containing tests and
                                 results
                                 in the following format:
                                 {"test_file1": [[x1, params1, results1],
                                                 [x2, params2, results2],
                                                  ...],
                                  "test_file2": ...}
        :type evaluations_file: string
        """

        assert (evaluations_file is not None), \
            'No function evaluations provided to test against for {}'.format(
                file_format)

        with open(evaluations_file, 'r') as ef:
            results = load(ef)

        format_dir = os.path.dirname(evaluations_file)

        for f, tests in results.items():
            f = os.path.join(format_dir, f)

            parser = ParserFactory.create_parser(f)
            with parser(f) as p:
                fitting_problem = p.parse()

            for r in tests:
                for i in range(len(fitting_problem.functions)):
                    actual = fitting_problem.eval_f(x=np.array(r[0]),
                                                    params=r[1],
                                                    function_id=i)
                    assert np.isclose(actual, r[2]).all()

    def test_factory(self, file_format, test_file):
        """
        Tests that the factory selects the correct parser

        :param file_format: The name of the file format
        :type file_format: string
        :param test_file: The path to the test file
        :type test_file: string
        """

        parser = ParserFactory.create_parser(test_file)
        assert (parser.__name__.lower().startswith(file_format.lower())), \
            'Factory failed to get associated parser for {}'.format(test_file)
