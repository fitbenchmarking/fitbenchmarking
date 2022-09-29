"""
This is a command line tool for handling checkpoint files for the
FitBenchmarking software package.
For more information on usage type fitbenchmarking --help
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

import sys
import textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from fitbenchmarking.core.results_output import save_results
from fitbenchmarking.utils.checkpoint import Checkpoint
from fitbenchmarking.utils.options import find_options_file


def get_parser() -> ArgumentParser:
    """
    Creates and returns a parser for the args.

    :return: Configured argument parser
    :rtype: ArgumentParser
    """

    description = (
        'This is a tool for working with checkpoint files generated during a'
        'FitBenchmarking run.'
    )

    parser = ArgumentParser(
        prog='fitbenchmarking-cp', add_help=True, description=description,
        formatter_class=RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='subprog')

    report_epilog = textwrap.dedent('''
    Usage Examples:

        $ fitbenchmarking-cp report
        $ fitbenchmarking-cp report -o examples/options_template.ini
        $ fitbenchmarking-cp report -f results/checkpoint
    ''')
    report = subparsers.add_parser(
        'report',
        description='Generate a report from a checkpoint file',
        epilog=report_epilog,
        add_help=True)
    report.add_argument('-f', '--filename',
                        metavar='CHECKPOINT_FILE',
                        default='',
                        help='The path to a fitbenchmarking checkpoint file')
    report.add_argument('-o', '--options-file',
                        metavar='OPTIONS_FILE',
                        default='',
                        help='The path to a fitbenchmarking options file')

    return parser


def generate_report(options_file='', additional_options=None):
    """
    Generate the fitting reports and tables for a checkpoint file.

    :param options_file: Path to an options file, defaults to ''
    :type options_file: str, optional
    :param additional_options: Extra options for the reporting.
                               Available keys are:
                                   filename (str): The checkpoint file to use.
    :type additional_options: dict, optional
    """
    if additional_options is not None:
        additional_options = {}

    options = find_options_file(options_file=options_file,
                                         additional_options=additional_options)

    checkpoint = Checkpoint(options=options)
    label, results, unselected_minimizers, failed_problems = checkpoint.load()

    save_results(group_name=label,
                 results=results,
                 options=options,
                 failed_problems=failed_problems,
                 unselected_minimizers=unselected_minimizers)


def main():
    """
    Entry point exposed as the `fitbenchmarking-cp` command.
    """
    parser = get_parser()

    args = parser.parse_args(sys.argv[1:])

    additional_options = {}

    if args.subprog == 'report':
        if args.filename:
            additional_options['checkpoint_filename'] = args.filename
        generate_report(args.options_file, additional_options)


if __name__ == '__main__':
    main()
