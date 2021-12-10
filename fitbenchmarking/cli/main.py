"""
This is the main entry point into the FitBenchmarking software package.
For more information on usage type fitbenchmarking --help
or for more general information, see the online docs at
docs.fitbenchmarking.com.
"""

from __future__ import absolute_import, division, print_function

import argparse
from distutils.dir_util import copy_tree
import glob
import inspect
import os
import platform
import sys
import webbrowser

from tempfile import NamedTemporaryFile
from jinja2 import Environment, FileSystemLoader

import fitbenchmarking
from fitbenchmarking.cli.exception_handler import exception_handler
from fitbenchmarking.core.fitting_benchmarking import benchmark
from fitbenchmarking.core.results_output import save_results
from fitbenchmarking.utils.exceptions import OptionsError, NoResultsError
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

    $ fitbenchmarking
    $ fitbenchmarking -p examples/benchmark_problems/NIST/*
    $ fitbenchmarking -o examples/options_template.ini \
    -p examples/benchmark_problems/CUTEst \
    examples/benchmark_problems/NIST/low_difficulty

Runtimes for these usage examples are approximately \
75, 200 and 90 seconds respectively (on an i7 core laptop \
with 32GB RAM)

Please note that the third listed example assumes that \
Fitbenchmarking has been installed with a number of pip \
installable fitting software packages. For more information \
on installing these packages, please see the Installation pages \
of the Fitbenchmarking docs. '''

    parser = argparse.ArgumentParser(
        prog='FitBenchmarking', add_help=True, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    root = os.path.dirname(inspect.getfile(fitbenchmarking))

    parser.add_argument('-o', '--options-file',
                        metavar='OPTIONS_FILE',
                        default='',
                        help='The path to a %(prog)s options file')
    parser.add_argument('-p', '--problem_sets',
                        nargs='+',
                        default=glob.glob(os.path.join(root,
                                                       'benchmark_problems',
                                                       'NIST',
                                                       'average_difficulty')),
                        help='Paths to directories containing problem sets.')
    parser.add_argument('-r', '--results-dir',
                        metavar='RESULTS_DIR',
                        default='',
                        help='The directory to store resulting files in.')
    parser.add_argument('-d', '--debug-mode',
                        default=False,
                        action='store_true',
                        help='Enable debug mode (prints traceback)',)

    return parser


def _find_options_file(options_file: str, results_directory: str) -> Options:
    """
    Attempts to find the options file and creates an Options object for it.
    Wildcards are accepted in the parameters of this function.

    :param options_file: The path or glob pattern for an options file.
    :type options_file: str
    :param results_directory: The path to the results directory.
    :type results_directory: str
    :return: An Options object.
    :rtype: fitbenchmarking.utils.options.Options
    """
    if options_file != '':
        # Read custom minimizer options from file
        glob_options_file = glob.glob(options_file)

        if not glob_options_file:
            raise OptionsError('Could not find file {}'.format(options_file))
        if not options_file.endswith(".ini"):
            raise OptionsError('Options file must be a ".ini" file')

        return Options(file_name=glob_options_file,
                       results_directory=results_directory)
    return Options(results_directory=results_directory)


def _create_index_page(options: Options, groups: "list[str]",
                       result_directories: "list[str]") -> str:
    """
    Creates the results index page for the benchmark, and copies
    the fonts and js directories to the correct location.

    :param options: The user options for the benchmark.
    :type options: fitbenchmarking.utils.options.Options
    :param groups: Names for each of the problem set groups.
    :type groups: A list of strings.
    :param result_directories: Result directory paths for each
    problem set group.
    :type result_directories: A list of strings.
    :return: The filepath of the `results_index.html` file.
    :rtype: str
    """
    root = os.path.dirname(inspect.getfile(fitbenchmarking))
    template_dir = os.path.join(root, "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    css = get_css(options, options.results_dir)
    template = env.get_template("index_page.html")
    group_links = [os.path.join(d, f"{g}_index.html")
                   for g, d in zip(groups, result_directories)]
    output_file = os.path.join(options.results_dir, 'results_index.html')

    # Copying fonts directory into results directory
    copy_tree(os.path.join(root, "fonts"),
              os.path.join(options.results_dir, "fonts"))
    # Copying js directory into results directory
    copy_tree(os.path.join(template_dir, "js"),
              os.path.join(options.results_dir, "js"))
    # Copying css directory into results directory
    copy_tree(os.path.join(template_dir, "css"),
              os.path.join(options.results_dir, "css"))

    with open(output_file, "w") as fh:
        fh.write(template.render(
            css_style_sheet=css["main"],
            custom_style=css["custom"],
            groups=groups,
            group_link=group_links,
            zip=zip))

    return output_file


def _open_browser(output_file: str) -> None:
    """
    Opens a browser window to show the results of a fit benchmark.

    :param output_file: The absolute path to the results index file.
    :type output_file: str
    """
    # Uses the relative path so that the browser can open on Mac and WSL
    relative_path = os.path.relpath(output_file)
    # Constructs a url that can be pasted into a browser
    is_mac = platform.system() == "Darwin"
    url = "file://" + output_file if is_mac else output_file

    if webbrowser.open_new(url if is_mac else relative_path):
        LOGGER.info("\nINFO:\nThe FitBenchmarking results have been opened "
                    "in your browser from this url:\n\n   %s", url)
    else:
        LOGGER.warning("\nWARNING:\nThe browser failed to open "
                       "automatically. Copy and paste the following url "
                       "into your browser:\n\n   %s", url)


@exception_handler
def run(problem_sets, results_directory, options_file='', debug=False):
    # pylint: disable=unused-argument
    """
    Run benchmarking for the problems sets and options file given.
    Opens a webbrowser to the results_index after fitting.

    :param problem_sets: The paths to directories containing problem_sets
    :type problem_sets: list of str
    :param results_directory: The directory to store the resulting files in
    :type results_directory: str
    :param options_file: The path to an options file, defaults to ''
    :type options_file: str, optional
    :param debug: Enable debugging output
    :type debug: bool
    """
    # Find the options file
    current_path = os.path.abspath(os.path.curdir)
    options = _find_options_file(options_file, results_directory)

    setup_logger(log_file=options.log_file,
                 append=options.log_append,
                 level=options.log_level)

    with NamedTemporaryFile(suffix='.ini', mode='w',
                            delete=False) as opt_file:
        options.write_to_stream(opt_file)
        opt_file_name = opt_file.name

    LOGGER.debug("The options file used is as follows:")
    with open(opt_file_name) as f:
        for line in f:
            LOGGER.debug(line.replace("\n", ""))
    os.remove(opt_file_name)

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
        results, failed_problems, unselected_minimizers = \
            benchmark(options=options,
                      data_dir=data_dir)

        # If a result has error flag 4 then the result contains dummy values,
        # if this is the case for all results then output should not be
        # produced as results tables won't show meaningful values.
        all_dummy_results_flag = True
        for result in results:
            if result.error_flag != 4:
                all_dummy_results_flag = False
                break

        # If the results are an empty list then this means that all minimizers
        # raise an exception and the tables will produce errors if they run
        # for that problem set.
        if results == [] or all_dummy_results_flag is True:
            message = "\nWARNING: \nThe user chosen options and/or problem " \
                      " setup resulted in all minimizers and/or parsers " \
                      "raising an exception. Because of this, results for " \
                      "the {} problem set will not be displayed. " \
                      "Please see the logs for more detail on why this is " \
                      "the case.".format(label)
            LOGGER.warning(message)
        else:
            LOGGER.info('Producing output for the %s problem set', label)
            # Display the runtime and accuracy results in a table
            group_results_dir = \
                save_results(group_name=label,
                             results=results,
                             options=options,
                             failed_problems=failed_problems,
                             unselected_minimizers=unselected_minimizers)

            LOGGER.info('Completed benchmarking for %s problem set', sub_dir)
            group_results_dir = os.path.relpath(path=group_results_dir,
                                                start=options.results_dir)
            result_dir.append(group_results_dir)
            groups.append(label)

        # resets options to original values
        options.reset()

    # Check result_dir is non empty before producing output
    if not result_dir:
        message = "The user chosen options and/or problem setup resulted in " \
                  "all minimizers and/or parsers raising an exception. " \
                  "For more detail on what caused this, please see the " \
                  "above logs before reviewing your options setup " \
                  "and/or problem set then re-run FitBenchmarking"
        raise NoResultsError(message)

    if results_directory == "":
        LOGGER.info("\nINFO:\nThe FitBenchmarking results will be placed "
                    "into the folder:\n\n   %s\n\nTo change this use the "
                    "-r or --results-dir optional command line argument. "
                    "You can also set 'results_dir' in an options file.",
                    options.results_dir)

    index_page = _create_index_page(options, groups, result_dir)
    _open_browser(index_page)


def main():
    """
    Entry point to be exposed as the `fitbenchmarking` command.
    """
    parser = get_parser()

    if len(sys.argv) == 1:
        print("Running NIST average_difficulty problem set "
              "with scipy minimizers \n")

    args = parser.parse_args(sys.argv[1:])

    run(problem_sets=args.problem_sets,
        results_directory=args.results_dir,
        options_file=args.options_file,
        debug=args.debug_mode)


if __name__ == '__main__':
    main()
