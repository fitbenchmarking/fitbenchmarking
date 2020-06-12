"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import absolute_import, division, print_function

import timeit
import warnings

import numpy as np

from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian
from fitbenchmarking.utils import fitbm_result, misc, output_grabber
from fitbenchmarking.utils.exceptions import NoResultsError, \
    UnknownMinimizerError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def benchmark(group_name, options, data_dir):
    """
    Gather the user input and list of paths. Call benchmarking on these.
    The benchmarking structure is:

    .. code-block:: python

        loop_over_benchmark_problems()
            loop_over_starting_values()
                loop_over_software()
                    loop_over_minimizers()

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

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    #################################
    # Loops over benchmark problems #
    #################################
    results, failed_problems, unselected_minimzers = \
        loop_over_benchmark_problems(problem_group, options)

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


def loop_over_benchmark_problems(problem_group, options):
    """
    Loops over benchmark problems

    :param problem_group: locations of the benchmark problem files
    :type problem_group: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

    :return: prob_results array of fitting results for the problem group,
             list of failed problems and dictionary of unselected minimizers
    :rtype: tuple(list, list, dict)
    """

    grabbed_output = output_grabber.OutputGrabber(options)
    results = []
    failed_problems = []
    for i, p in enumerate(problem_group):
        with grabbed_output:
            parsed_problem = parse_problem_file(p, options)
        parsed_problem.correct_data()

        # Creates Jacobian class
        jacobian_cls = create_jacobian(options)
        jacobian = jacobian_cls(parsed_problem)

        # Making the Jacobian class part of the fitting problem. This will
        # eventually be extended to have Hessian information too.
        parsed_problem.jac = jacobian

        name = parsed_problem.name

        info_str = " Running data from: {} {}/{}".format(
            name, i + 1, len(problem_group))
        LOGGER.info('#' * (len(info_str) + 1))
        LOGGER.info(info_str)
        LOGGER.info('#' * (len(info_str) + 1))

        ##############################
        # Loops over starting values #
        ##############################
        problem_results, problem_fails, unselected_minimzers = \
            loop_over_starting_values(parsed_problem, options)

        results.extend(problem_results)
        failed_problems.extend(problem_fails)

    return results, failed_problems, unselected_minimzers


def loop_over_starting_values(problem, options):
    """
    Loops over starting values from the fitting problem

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

    :return: prob_results array of fitting results for the problem group,
             list of failed problems and dictionary of unselected minimizers
    :rtype: tuple(list, list, dict)
    """
    name = problem.name
    num_start_vals = len(problem.starting_values)
    problem_results = []
    for index in range(num_start_vals):
        LOGGER.info("    Starting value: {0}/{1}".format(index + 1,
                                                         num_start_vals))
        if num_start_vals > 1:
            problem.name = name + ', Start {}'.format(index + 1)

        ################################
        # Loops over fitting softwares #
        ################################
        individual_problem_results, problem_fails, unselected_minimzers = \
            loop_over_fitting_software(problem=problem,
                                       options=options,
                                       start_values_index=index)
        problem_results.extend(individual_problem_results)

    return problem_results, problem_fails, unselected_minimzers


def loop_over_fitting_software(problem, options, start_values_index):
    """
    Loops over fitting software selected in the options

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

    :return: list of all results, failed problem names and dictionary of
             unselected minimizers based on algorithm_type
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  list of failed problem names,
                  dictionary of minimizers)
    """
    grabbed_output = output_grabber.OutputGrabber(options)
    results = []

    software = options.software
    if not isinstance(software, list):
        software = [software]

    problem_fails = []
    unselected_minimzers = {}
    software_results = []
    for s in software:
        LOGGER.info("        Software: %s", s.upper())
        try:
            minimizers = options.minimizers[s]
        except KeyError:
            raise UnknownMinimizerError(
                'No minimizer given for software: {}'.format(s))
        with grabbed_output:
            controller_cls = ControllerFactory.create_controller(
                software=s)
            controller = controller_cls(problem=problem)

        controller.parameter_set = start_values_index

        #########################
        # Loops over minimizers #
        #########################
        problem_result, minimizer_failed = \
            loop_over_minimizers(controller=controller,
                                 minimizers=minimizers,
                                 options=options)
        unselected_minimzers[s] = minimizer_failed
        software_results.extend(problem_result)

    # Checks to see if all of the minimizers raise and exception and
    # records the problems name for that case
    software_check = [np.isinf(v.chi_sq) for v in software_results]
    if all(software_check):
        software_results = []
        problem_fails.append(problem.name)
    results.extend(software_results)

    return results, problem_fails, unselected_minimzers


def loop_over_minimizers(controller, minimizers, options):
    """
    Loops over minimizers in fitting software

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param minimizers: array of minimizers used in fitting
    :type minimizers: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

    :return: list of all results and dictionary of unselected minimizers
             based on algorithm_type
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  list of failed minimizers)
    """
    grabbed_output = output_grabber.OutputGrabber(options)
    problem = controller.problem
    jac = controller.problem.jac

    results_problem = []
    minimizer_failed = []

    num_runs = options.num_runs
    algorithm_type = options.algorithm_type

    for minimizer in minimizers:
        minimizer_check = True
        LOGGER.info("            Minimizer: %s", minimizer)

        controller.minimizer = minimizer
        try:
            with grabbed_output:
                controller.validate_minimizer(minimizer, algorithm_type)
                # Calls timeit repeat with repeat = num_runs and number = 1
                runtime_list = \
                    timeit.Timer(setup=controller.prepare,
                                 stmt=controller.fit).repeat(num_runs, 1)
                runtime = sum(runtime_list) / num_runs
                controller.cleanup()
        # Catching all exceptions as this means runtime cannot be calculated
        # pylint: disable=broad-except
        except Exception as excp:
            if isinstance(excp, UnknownMinimizerError):
                minimizer_failed.append(minimizer)
                minimizer_check = False
            LOGGER.warn(str(excp))

            runtime = np.inf
            controller.flag = 3
            controller.final_params = None if not problem.multifit \
                else [None] * len(controller.data_x)
            chi_sq = np.inf if not problem.multifit \
                else [np.inf] * len(controller.data_x)

        controller.check_attributes()

        if controller.flag <= 2:
            ratio = np.max(runtime_list) / np.min(runtime_list)
            tol = 4
            if ratio > tol:
                warnings.warn('The ratio of the max time to the min is {0}'
                              ' which is  larger than the tolerance of {1},'
                              ' which may indicate that caching has occurred'
                              ' in the timing results'.format(ratio, tol))
            chi_sq = controller.eval_chisq(params=controller.final_params,
                                           x=controller.data_x,
                                           y=controller.data_y,
                                           e=controller.data_e)

        result_args = {'options': options,
                       'problem': problem,
                       'jac': jac,
                       'chi_sq': chi_sq,
                       'runtime': runtime,
                       'minimizer': minimizer,
                       'initial_params': controller.initial_params,
                       'params': controller.final_params,
                       'error_flag': controller.flag,
                       'name': problem.name}
        if minimizer_check:
            if problem.multifit:
                # Multi fit (will raise TypeError if these are not iterable)
                for i in range(len(chi_sq)):
                    result_args.update({'dataset_id': i,
                                        'name': '{}, Dataset {}'.format(
                                            problem.name, (i + 1))})
                    individual_result = \
                        fitbm_result.FittingResult(**result_args)
                    results_problem.append(individual_result)
            else:
                # Normal fitting
                individual_result = fitbm_result.FittingResult(**result_args)
                results_problem.append(individual_result)
    return results_problem, minimizer_failed
