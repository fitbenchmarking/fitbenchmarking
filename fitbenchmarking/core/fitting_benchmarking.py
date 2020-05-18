"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import absolute_import, division, print_function

from fitbenchmarking.core.fitbenchmark_one_problem import fitbm_one_prob
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import misc, output_grabber
from fitbenchmarking.utils.exceptions import NoResultsError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def fitbenchmark_group(group_name, options, data_dir):
    """
    Gather the user input and list of paths. Call benchmarking on these.

    :param group_name: is the name (label) for a group. E.g. the name for
                       the group of problems in "NIST/low_difficulty" may be
                       picked to be NIST_low_difficulty
    :type group_name: str
    :param options: dictionary containing software used in fitting
                    the problem, list of minimizers and location of
                    json file contain minimizers
    :type options: fitbenchmarking.utils.options.Options
    :param data_dir: full path of a directory that holds a group of problem
                     definition files
    :type date_dir: str

    :return: prob_results array of fitting results for the problem group,
             list of failed problems and dictionary of unselected minimizers
    :rtype: tuple(list, list, dict)
    """
    grabbed_output = output_grabber.OutputGrabber(options)

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    results = []

    failed_problems = []
    for i, p in enumerate(problem_group):
        with grabbed_output:
            parsed_problem = parse_problem_file(p, options)
        parsed_problem.correct_data()
        name = parsed_problem.name

        info_str = " Running data from: {} {}/{}".format(
            name, i + 1, len(problem_group))
        LOGGER.info('#' * (len(info_str) + 1))
        LOGGER.info(info_str)
        LOGGER.info('#' * (len(info_str) + 1))

        problem_results, problem_fails, unselected_minimzers = \
            fitbm_one_prob(problem=parsed_problem,
                           options=options)
        results.extend(problem_results)
        failed_problems.extend(problem_fails)

    for keys, minimzers in unselected_minimzers.items():
        minimizers_all = options.minimizers[keys]
        options.minimizers[keys] = list(set(minimizers_all) - set(minimzers))

    # options.minimizers = converge_minimizers
    # If the results are and empty list then this means that all minimizers
    # raise an exception and the tables will produce errors if they run.
    if results == []:
        message = "The current options set up meant that all minimizers set " \
                  "raised an exception. This is likely due to the " \
                  "`algorithm_type` set in the options. Please review " \
                  "current options setup and re-run FitBenmarking."
        raise NoResultsError(message)

    # Used to group elements in list by name
    results_dict = {}
    for problem_result in results:
        name = problem_result.name
        # group by name
        try:
            results_dict[name].append(problem_result)
        except KeyError:
            results_dict[name] = [problem_result]

    results = [results_dict[r] for r in
               sorted(results_dict.keys(), key=str.lower)]

    return results, failed_problems, unselected_minimzers
