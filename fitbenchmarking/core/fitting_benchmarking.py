"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import (absolute_import, division, print_function)

from fitbenchmarking.utils.logging_setup import logger

from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import misc
from fitbenchmarking.utils import output_grabber
from fitbenchmarking.core.fitbenchmark_one_problem import fitbm_one_prob


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

    :return: prob_results array of fitting results for
             the problem group and the location of the results
    :rtype: tuple(list, str)
    """
    grabbed_output = output_grabber.OutputGrabber()

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    results = []
    template_prob_name = " Running data from: {}"
    for i, p in enumerate(problem_group):
        with grabbed_output:
            parsed_problem = parse_problem_file(p, options)
            parsed_problem.correct_data(options.use_errors)

        decorator = '#' * (len(template_prob_name) +
                           len(parsed_problem.name) + 4)
        tmp_prob_name = template_prob_name.format(parsed_problem.name)
        print("\n{0}\n{1} {2}/{3}\n{0}\n".format(decorator, tmp_prob_name,
                                                 i + 1, len(problem_group)))

        problem_results = fitbm_one_prob(problem=parsed_problem,
                                         options=options)

        # Convert from list of dict to list of list and store
        for r in problem_results:
            tmp_result = []
            for s in options.software:
                tmp_result.extend(r[s])
            results.append(tmp_result)

    return results
