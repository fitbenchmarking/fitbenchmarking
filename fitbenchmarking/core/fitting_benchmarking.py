"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import absolute_import, division, print_function

from collections import defaultdict
import timeit
import warnings

import numpy as np

from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils.exceptions import NoResultsError, \
    UnknownMinimizerError, UnsupportedMinimizerError
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian, \
    get_jacobian_options
from fitbenchmarking.utils import fitbm_result, misc, output_grabber

from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def benchmark(options, data_dir):
    """
    Gather the user input and list of paths. Call benchmarking on these.
    The benchmarking structure is:

    .. code-block:: python

        loop_over_benchmark_problems()
            loop_over_starting_values()
                loop_over_software()
                    loop_over_minimizers()
                        loop_over_jacobians()

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
    results, failed_problems, unselected_minimzers, minimizer_dict = \
        loop_over_benchmark_problems(problem_group, options)

    for keys, minimzers in unselected_minimzers.items():
        minimizers_all = options.minimizers[keys]
        options.minimizers[keys] = list(set(minimizers_all) - set(minimzers))

    options.minimizers = minimizer_dict
    # If the results are an empty list then this means that all minimizers
    # raise an exception and the tables will produce errors if they run.
    if results == []:
        message = "The user chosen options setup resulted in all minimizers " \
                  "raising an exception. This is likely due to the way " \
                  "`algorithm_type` was set in the options. Please review " \
                  "your options setup and re-run FitBenmarking."
        raise NoResultsError(message)

    # Used to group elements in list by name
    results_dict = defaultdict(list)
    for problem_result in results:
        results_dict[problem_result.name].append(problem_result)

    results = [results_dict[r] for r in
               sorted(results_dict.keys(), key=lambda x: x.lower())]

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

        name = parsed_problem.name

        info_str = " Running data from: {} {}/{}".format(
            name, i + 1, len(problem_group))
        LOGGER.info('\n' + '#' * (len(info_str) + 1))
        LOGGER.info(info_str)
        LOGGER.info('#' * (len(info_str) + 1))

        ##############################
        # Loops over starting values #
        ##############################
        problem_results, problem_fails, \
            unselected_minimzers, minimizer_dict = \
            loop_over_starting_values(parsed_problem, options, grabbed_output)

        results.extend(problem_results)
        failed_problems.extend(problem_fails)
    return results, failed_problems, unselected_minimzers, minimizer_dict


def loop_over_starting_values(problem, options, grabbed_output):
    """
    Loops over starting values from the fitting problem

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

    :return: prob_results array of fitting results for the problem group,
             list of failed problems, dictionary of unselected minimizers and
             dictionary of minimizers together with the Jacobian used
    :rtype: tuple(list, list, dict, dict)
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
        individual_problem_results, problem_fails, \
            unselected_minimzers, minimizer_dict = \
            loop_over_fitting_software(problem=problem,
                                       options=options,
                                       start_values_index=index,
                                       grabbed_output=grabbed_output)
        problem_results.extend(individual_problem_results)

    return problem_results, problem_fails, unselected_minimzers, minimizer_dict


def loop_over_fitting_software(problem, options, start_values_index,
                               grabbed_output):
    """
    Loops over fitting software selected in the options

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param start_values_index: Integer that selects the starting values when
                               datasets have multiple ones.
    :type start_values_index: int
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

    :return: list of all results, failed problem names, dictionary of
             unselected minimizers based on algorithm_type and
             dictionary of minimizers together with the Jacobian used
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  list of failed problem names,
                  dictionary of minimizers.
                  dictionary of minimizers and Jacobians)
    """
    results = []
    software = options.software
    if not isinstance(software, list):
        software = [software]

    problem_fails = []
    unselected_minimzers = {}
    minimizer_dict = {}
    software_results = []
    for s in software:
        LOGGER.info("        Software: %s", s.upper())
        try:
            minimizers = options.minimizers[s]
        except KeyError:
            raise UnsupportedMinimizerError(
                'No minimizer given for software: {}'.format(s))
        with grabbed_output:
            controller_cls = ControllerFactory.create_controller(
                software=s)
            controller = controller_cls(problem=problem)

        controller.parameter_set = start_values_index

        #########################
        # Loops over minimizers #
        #########################
        problem_result, minimizer_failed, new_minimizer_list = \
            loop_over_minimizers(controller=controller,
                                 minimizers=minimizers,
                                 options=options,
                                 grabbed_output=grabbed_output)

        unselected_minimzers[s] = minimizer_failed
        minimizer_dict[s] = new_minimizer_list
        software_results.extend(problem_result)

    # Checks to see if all of the minimizers from every software raised an
    # exception and record the problem name if that is the case
    software_check = [np.isinf(v.chi_sq) for v in software_results]
    if all(software_check):
        software_results = []
        problem_fails.append(problem.name)
    results.extend(software_results)

    return results, problem_fails, unselected_minimzers, minimizer_dict


def loop_over_minimizers(controller, minimizers, options, grabbed_output):
    """
    Loops over minimizers in fitting software

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param minimizers: array of minimizers used in fitting
    :type minimizers: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

    :return: list of all results, dictionary of unselected minimizers
             based on algorithm_type and dictionary of minimizers together
             with the Jacobian used
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  list of failed minimizers,
                  list of minimizers and Jacobians)
    """
    problem = controller.problem
    algorithm_type = options.algorithm_type

    results_problem = []
    minimizer_failed = []
    new_minimizer_list = []
    for minimizer in minimizers:
        controller.minimizer = minimizer
        minimizer_check = True
        LOGGER.info("            Minimizer: %s", minimizer)
        try:
            controller.validate_minimizer(minimizer, algorithm_type)
        except UnknownMinimizerError as excp:
            minimizer_failed.append(minimizer)
            minimizer_check = False
            LOGGER.warn(str(excp))

        if minimizer_check:
            ########################
            # Loops over Jacobians #
            ########################
            results, chi_sq, minimizer_list = \
                loop_over_jacobians(controller,
                                    options,
                                    grabbed_output)
            for result in results:
                if problem.multifit:
                    # Multi fit (will raise TypeError if these are not iterable)
                    for i in range(len(chi_sq)):
                        result.update({'dataset_id': i,
                                       'name': '{}, Dataset {}'.format(
                                           problem.name, (i + 1))})
                        individual_result = \
                            fitbm_result.FittingResult(**result)
                        results_problem.append(individual_result)
                else:
                    # Normal fitting
                    individual_result = fitbm_result.FittingResult(
                        **result)
                    results_problem.append(individual_result)
            new_minimizer_list.extend(minimizer_list)

    return results_problem, minimizer_failed, new_minimizer_list


def loop_over_jacobians(controller, options, grabbed_output):
    """
    Loops over Jacobians set from the options file

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

    :return: list of all results, dictionary of unselected minimizers
             based on algorithm_type and dictionary of minimizers together
             with the Jacobian used
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  list of failed minimizers,
                  list of minimizers and Jacobians)
    """
    problem = controller.problem
    minimizer = controller.minimizer
    num_runs = options.num_runs
    has_jacobian, invalid_jacobians = controller.jacobian_information()
    jacobian_list = get_jacobian_options(options)
    minimizer_name = minimizer
    results = []
    new_minimizer_list = []
    for jac_name in jacobian_list:
        jac_method, num_method = jac_name
        if (has_jacobian and minimizer not in invalid_jacobians):
            LOGGER.info("                Jacobian: %s %s", jac_method,
                        num_method)
            minimizer_name = "{}: {} {}".format(
                minimizer, jac_method, num_method)
        # Creates Jacobian class
        jacobian_cls = create_jacobian(jac_method, num_method)
        jacobian = jacobian_cls(problem)
        controller.jacobian = jacobian

        try:
            with grabbed_output:
                # Calls timeit repeat with repeat = num_runs and
                # number = 1
                runtime_list = \
                    timeit.Timer(setup=controller.prepare,
                                 stmt=controller.fit).repeat(
                        num_runs, 1)
                runtime = sum(runtime_list) / num_runs
                controller.cleanup()
        # Catching all exceptions as this means runtime cannot be
        # calculated
        # pylint: disable=broad-except
        except Exception as excp:
            LOGGER.warn(str(excp))

            runtime = np.inf
            controller.flag = 3
            controller.final_params = None if not problem.multifit \
                else [None] * len(controller.data_x)

        controller.check_attributes()
        if controller.flag <= 2:
            ratio = np.max(runtime_list) / np.min(runtime_list)
            tol = 4
            if ratio > tol:
                warnings.warn(
                    'The ratio of the max time to the min is {0}'
                    ' which is  larger than the tolerance of {1},'
                    ' which may indicate that caching has occurred'
                    ' in the timing results'.format(ratio, tol))
            chi_sq = controller.eval_chisq(
                params=controller.final_params,
                x=controller.data_x,
                y=controller.data_y,
                e=controller.data_e)
        else:
            chi_sq = np.inf if not problem.multifit \
                else [np.inf] * len(controller.data_x)
        result_args = {'options': options,
                       'problem': problem,
                       'jac': jacobian,
                       'chi_sq': chi_sq,
                       'runtime': runtime,
                       'minimizer': minimizer_name,
                       'initial_params': controller.initial_params,
                       'params': controller.final_params,
                       'error_flag': controller.flag,
                       'name': problem.name}
        results.append(result_args)
        new_minimizer_list.append(minimizer_name)
        if not has_jacobian or minimizer in invalid_jacobians:
            break
    return results, chi_sq, new_minimizer_list
