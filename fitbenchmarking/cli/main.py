"""
This is the main entry point into the FitBenchmarking software package.
For more information on usage type fitbenchmarking --help
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

from __future__ import absolute_import, division, print_function

import argparse
import glob
import inspect
import os
import sys
import webbrowser

from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.cli.exception_handler import exception_handler
from fitbenchmarking.core.fitting_benchmarking import benchmark
from fitbenchmarking.core.results_output import save_results
from fitbenchmarking.utils.exceptions import OptionsError
from fitbenchmarking.utils.log import get_logger, setup_logger
from fitbenchmarking.utils.misc import get_css
from fitbenchmarking.utils.options import Options

LOGGER = get_logger()


def get_parser():
    """
    Creates and returns a parser for the args.

    :return: configured argument parser
    :rtype: argparse.ArgParser
    """

    epilog = '''Usage Examples:

    $ fitbenchmarking examples/benchmark_problems/NIST/*
    $ fitbenchmarking -o examples/options_template.ini \
examples/benchmark_problems/simple_tests examples/benchmark_problems/Muon '''

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
    parser.add_argument('-d', '--debug-mode',
                        default=False,
                        action='store_true',
                        help='Enable debug mode (prints traceback)',)

    return parser


@exception_handler
def run(problem_sets, options_file='', debug=False):
    """
    Run benchmarking for the problems sets and options file given.
    Opens a webbrowser to the results_index after fitting.

    :param problem_sets: The paths to directories containing problem_sets
    :type problem_sets: list of str
    :param options_file: The path to an options file, defaults to ''
    :type options_file: str, optional
    :param debug: Enable debugging output
    :type debug: bool
    """
    # Find the options file
    current_path = os.path.abspath(os.path.curdir)
    if options_file != '':
        # Read custom minimizer options from file
        glob_options_file = glob.glob(options_file)
        if glob_options_file == []:
            raise OptionsError('Could not find file {}'.format(options_file))
        if not options_file.endswith(".ini"):
            raise OptionsError('Options file must be a ".ini" file')
        else:
            options = Options(glob_options_file)
    else:
        options = Options()

    setup_logger(log_file=options.log_file,
                 append=options.log_append,
                 level=options.log_level)

    groups = []
    result_dir = []
    for sub_dir in problem_sets:

        # Create full path for the directory that holds a group of
        # problem definition files
        data_dir = os.path.join(current_path, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            LOGGER.warning('Problem set %s not found', data_dir)
            continue

        # generate group label/name used for problem set
        try:
            with open(os.path.join(data_dir, 'META.txt'), 'r') as f:
                label = f.readline().strip('\n')
        except IOError:
            label = sub_dir.replace('/', '_')

        LOGGER.info('Running the benchmarking on the %s problem set',
                    label)
        results, failed_problems, unselected_minimzers = \
            benchmark(options=options,
                      data_dir=data_dir)
        LOGGER.info('Producing output for the %s problem set', label)
        # Display the runtime and accuracy results in a table
        group_results_dir = \
            save_results(group_name=label,
                         results=results,
                         options=options,
                         failed_problems=failed_problems,
                         unselected_minimzers=unselected_minimzers)

        LOGGER.info('Completed benchmarking for %s problem set', sub_dir)
        group_results_dir = os.path.relpath(path=group_results_dir,
                                            start=options.results_dir)
        result_dir.append(group_results_dir)
        groups.append(label)

        # resets options to original values
        options.reset()

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options,options.results_dir)
    template = env.get_template("index_page.html")
    group_links = [os.path.join(d, "{}_index.html".format(g))
                   for g, d in zip(groups, result_dir)]
    output_file = os.path.join(options.results_dir, 'results_index.html')

    with open(output_file, 'w') as fh:
        fh.write(template.render(
            css_style_sheet=css['main'],
            custom_style=css['custom'],
            groups=groups,
            group_link=group_links,
            zip=zip))
    webbrowser.open_new(output_file)


def main():
    """
    Entry point to be exposed as the `fitbenchmarking` command.
    """
    parser = get_parser()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args(sys.argv[1:])

    run(problem_sets=args.problem_sets,
        options_file=args.options_file, debug=args.debug_mode)


if __name__ == '__main__':
    main()
