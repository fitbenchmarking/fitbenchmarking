"""
This file contains a factory implementation for the parsers.
This is used to manage the imports and reduce effort in adding new parsers.
"""

from importlib import import_module
from inspect import isclass, isabstract, getmembers

from fitbenchmarking.parsing.base_parser import Parser


class ParserFactory:
    """
    A factory for creating parsers.
    This has the capability to select the correct parser, import it, and
    generate an instance of it.
    Parsers generated from this must be a subclass of base_parser.Parser
    """

    @staticmethod
    def create_parser(filename):
        """
        Inspect the input and create a parser that matches the required file.

        :param filename: The path to the file to be parsed
        :type filename: string

        :returns: Parser for the problem
        :rtype: fitbenchmarking.parsing.base_parser.Parser subclass
        """

        with open(filename, 'r') as f:
            line = f.readline()

        # Take the first section of text
        module_name = ''
        for l in line.strip('#').strip():
            if not l.isalpha():
                break
            module_name += l

        module_name = '{}_parser'.format(module_name.lower())
        try:
            module = import_module('.' + module_name, __package__)
        except ImportError:
            raise ValueError('Could not find parser for {}.'.format(filename)
                             + 'Check the input is correct and try again.')

        classes = getmembers(module, lambda m: (isclass(m)
                                                and not isabstract(m)
                                                and issubclass(m, Parser)
                                                and m is not Parser))

        return classes[0][1]


def parse_problem_file(prob_file):
    """
    Loads the problem file into a fitting problem using the correct parser.

    :param prob_file: path to the problem file
    :type prob_file: string

    :returns: problem object with fitting information
    :rtype: fitbenchmarking.parsing.fitting_problem.FittingProblem
    """
    parser = ParserFactory.create_parser(prob_file)
    with parser(prob_file) as p:
        problem = p.parse()
    if not problem.verify():
        raise RuntimeError('Parsing failed.')

    return problem
