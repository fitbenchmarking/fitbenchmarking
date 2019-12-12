"""
This is the main entry point into the FitBenchmarking software package.
For more information on usage type fitbenchmarking --help 
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

from __future__ import (absolute_import, division, print_function)
import argparse
import glob
import os
import sys

from fitbenchmarking.fitting_benchmarking import fitbenchmark_group
from fitbenchmarking.results_output import save_results_tables
from fitbenchmarking.utils.options import Options


def get_parser():
    """
    Creates and returns a parser for the args.
    """

    epilog = '''Usage Examples:

    $ fitbenchmarking benchmark_problems/NIST/*
    $ fitbenchmarking -o myoptions.ini benchmark_problems/simple_tests \
benchmark_problems/Muon '''

    parser = argparse.ArgumentParser(
        prog='FitBenchmarking', add_help=True, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-o', '--options-file',
                        metavar='OPTIONS_FILE',
                        default='',
                        help='The path to a %(prog)s options file')
    parser.add_argument('problem_sets',
                        nargs='+',
                        help='Paths to directories containing problem sets.')

    return parser


def run(problem_sets, options_file=''):
    """
    Run benchmarking for the problems sets and options file given.

    :param problem_sets: The paths to directories containing problem_sets
    :type problem_sets: list of str
    :param options_file: he path to an options file, defaults to ''
    :type options_file: str, optional
    """

    # Find the options file
    current_path = os.path.abspath(os.path.curdir)
    if options_file != '':
        # Read custom minimizer options from file
        options_file = glob.glob(options_file)
        options = Options(options_file)
    else:
        options = Options()

    for sub_dir in problem_sets:
        # generate group label/name used for problem set
        label = sub_dir.replace('/', '_')

        # Create full path for the directory that holds a group of
        # problem definition files
        data_dir = os.path.join(current_path, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            print('Problem set {} not found'.format(data_dir))
            continue

        print('\nRunning the benchmarking on the {} problem set\n'.format(
            label))
        results = fitbenchmark_group(group_name=label,
                                     options=options,
                                     data_dir=data_dir)

        print('\nProducing output for the {} problem set\n'.format(label))
        # Display the runtime and accuracy results in a table
        save_results_tables(group_name=label,
                            results=results,
                            options=options)

        print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))


def main():
    """
    Entry point to be exposed as the `fitbenchmarking` command.
    """
    parser = get_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(sys.argv[1:])

    run(problem_sets=args.problem_sets, options_file=args.options_file)


if __name__ == '__main__':
    main()
