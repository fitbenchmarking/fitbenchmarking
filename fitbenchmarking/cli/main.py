"""
This is the main entry point into the FitBenchmarking software package.
For more information on usage type fitbenchmarking --help
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

from __future__ import (absolute_import, division, print_function)
import argparse
import glob
import inspect
from jinja2 import Environment, FileSystemLoader
import os
import sys
import webbrowser

import fitbenchmarking
from fitbenchmarking.core.fitting_benchmarking import fitbenchmark_group
from fitbenchmarking.core.results_output import save_results
from fitbenchmarking.utils.options import Options


def get_parser():
    """
    Creates and returns a parser for the args.
    """

    epilog = '''Usage Examples:

    $ fitbenchmarking examples/benchmark_problems/NIST/*
    $ fitbenchmarking -o examples/myoptions.ini \
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
        glob_options_file = glob.glob(options_file)
        if glob_options_file == [] or not options_file.endswith(".ini"):
            raise RuntimeError('Error in user input options file. Please check'
                               'that the file exist and has an .ini '
                               'extension, current path to file is '
                               '{}'.format(options_file))
        else:
            options = Options(glob_options_file)
    else:
        options = Options()
    groups = []
    result_dir = []
    for sub_dir in problem_sets:

        # Create full path for the directory that holds a group of
        # problem definition files
        data_dir = os.path.join(current_path, sub_dir)

        test_data = glob.glob(data_dir + '/*.*')

        if test_data == []:
            print('Problem set {} not found'.format(data_dir))
            continue

        # generate group label/name used for problem set
        try:
            with open(os.path.join(data_dir, 'META.txt'), 'r') as f:
                label = f.readline().strip('\n')
        except IOError:
            label = sub_dir.replace('/', '_')

        print('\nRunning the benchmarking on the {} problem set\n'.format(
            label))
        results = fitbenchmark_group(group_name=label,
                                     options=options,
                                     data_dir=data_dir)
        print('\nProducing output for the {} problem set\n'.format(label))
        # Display the runtime and accuracy results in a table
        group_results_dir = save_results(group_name=label,
                                         results=results,
                                         options=options)

        print('\nCompleted benchmarking for {} problem set\n'.format(sub_dir))
        group_results_dir = os.path.relpath(path=group_results_dir,
                                            start=options.results_dir)
        result_dir.append(group_results_dir)
        groups.append(label)

    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    html_page_dir = os.path.join(root, 'HTML_templates')
    env = Environment(loader=FileSystemLoader(html_page_dir))
    style_css = os.path.join(html_page_dir, 'main_style.css')
    custom_style = os.path.join(html_page_dir, 'custom_style.css')
    template = env.get_template("index_page.html")
    group_links = [os.path.join(d, "{}_index.html".format(g))
                   for g, d in zip(groups, result_dir)]
    output_file = os.path.join(options.results_dir, 'results_index.html')

    with open(output_file, 'w') as fh:
        fh.write(template.render(
            css_style_sheet=style_css,
            custom_style=custom_style,
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

    run(problem_sets=args.problem_sets, options_file=args.options_file)


if __name__ == '__main__':
    main()
