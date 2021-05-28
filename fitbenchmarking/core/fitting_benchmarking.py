"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import absolute_import, division, print_function

import os
import timeit
import warnings
from collections import defaultdict

import numpy as np

from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, misc, output_grabber
from fitbenchmarking.utils.exceptions import (FitBenchmarkException,
                                              ControllerAttributeError,
                                              IncompatibleMinimizerError,
                                              NoJacobianError,
                                              UnknownMinimizerError,
                                              UnsupportedMinimizerError)
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
             list of failed problems and dictionary of unselected minimizers,
             rst description of the cost function from the docstring
    :rtype: tuple(list, list, dict, str)
    """

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    #################################
    # Loops over benchmark problems #
    #################################
    results, failed_problems, unselected_minimzers, \
        minimizer_dict, cost_func_description = \
        loop_over_benchmark_problems(problem_group, options)

    options.minimizers = minimizer_dict

    # Used to group elements in list by name
    results_dict = defaultdict(list)
    for problem_result in results:
        results_dict[problem_result.name].append(problem_result)
    results = [results_dict[r] for r in
               sorted(results_dict.keys(), key=lambda x: x.lower())]
    return results, failed_problems, unselected_minimzers, \
        cost_func_description


def loop_over_benchmark_problems(problem_group, options):
    """
    Loops over benchmark problems

    :param problem_group: locations of the benchmark problem files
    :type problem_group: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

    :return: prob_results array of fitting results for the problem group,
             list of failed problems and dictionary of unselected minimizers,
             rst description of the cost function from the docstring
    :rtype: tuple(list, list, dict, str)
    """
    grabbed_output = output_grabber.OutputGrabber(options)
    results = []
    failed_problems = []
    for i, p in enumerate(problem_group):
        problem_passed = True
        info_str = " Running data from: {} {}/{}".format(
            os.path.basename(p), i + 1, len(problem_group))
        LOGGER.info('\n%s', '#' * (len(info_str) + 1))
        LOGGER.info(info_str)
        LOGGER.info('#' * (len(info_str) + 1))
        try:
            with grabbed_output:
                parsed_problem = parse_problem_file(p, options)
                parsed_problem.correct_data()
        except FitBenchmarkException as e:
            info_str = " Could not run data from: {} {}/{}".format(
                p, i + 1, len(problem_group))
            LOGGER.warning(e)
            problem_passed = False

        if problem_passed:
            ##############################
            # Loops over starting values #
            ##############################
            cost_func_cls = create_cost_func(options.cost_func_type)
            cost_func = cost_func_cls(parsed_problem)
            cost_func_description = cost_func.__doc__
            problem_results, problem_fails, \
                unselected_minimzers, minimizer_dict = \
                loop_over_starting_values(
                    cost_func, options, grabbed_output)
            results.extend(problem_results)
            failed_problems.extend(problem_fails)

    return results, failed_problems, unselected_minimzers, \
        minimizer_dict, cost_func_description


def loop_over_starting_values(cost_func, options, grabbed_output):
    """
    Loops over starting values from the fitting cost_func

    :param cost_func: a cost_func object containing information used in fitting
    :type cost_func: CostFunc
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

    :return: prob_results array of fitting results for the problem group,
             list of failed problems, dictionary of unselected minimizers and
             dictionary of minimizers together with the Jacobian used
    :rtype: tuple(list, list, dict, dict)
    """
    problem = cost_func.problem
    name = problem.name
    num_start_vals = len(problem.starting_values)
    problem_results = []
    for index in range(num_start_vals):
        LOGGER.info("    Starting value: %i/%i", index + 1, num_start_vals)
        if num_start_vals > 1:
            problem.name = name + ', Start {}'.format(index + 1)

        ################################
        # Loops over fitting softwares #
        ################################
        individual_problem_results, problem_fails, \
            unselected_minimzers, minimizer_dict = \
            loop_over_fitting_software(cost_func=cost_func,
                                       options=options,
                                       start_values_index=index,
                                       grabbed_output=grabbed_output)
        problem_results.extend(individual_problem_results)

    return problem_results, problem_fails, unselected_minimzers, minimizer_dict


def loop_over_fitting_software(cost_func, options, start_values_index,
                               grabbed_output):
    """
    Loops over fitting software selected in the options

    :param cost_func: a cost_func object containing information used in fitting
    :type cost_func: CostFunction
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
        except KeyError as e:
            raise UnsupportedMinimizerError(
                'No minimizer given for software: {}'.format(s)) from e
        with grabbed_output:
            controller_cls = ControllerFactory.create_controller(
                software=s)
            controller = controller_cls(cost_func=cost_func)

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
        problem_fails.append(cost_func.problem.name)
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
            LOGGER.warning(str(excp))

        try:
            controller.cost_func.validate_algorithm_type(
                controller.algorithm_check, minimizer)
        except IncompatibleMinimizerError as excp:
            minimizer_failed.append(minimizer)
            minimizer_check = False
            LOGGER.warning(str(excp))

        if controller.problem.value_ranges is not None:
            try:
                controller.check_minimizer_bounds(minimizer)
            except IncompatibleMinimizerError as excp:
                minimizer_check = False
                controller.flag = 4
                dummy_results = [{'options': options,
                                  'cost_func': controller.cost_func,
                                  'jac': None,
                                  'chi_sq': np.inf,
                                  'runtime': np.inf,
                                  'minimizer': minimizer,
                                  'initial_params': controller.initial_params,
                                  'params': None,
                                  'error_flag': controller.flag,
                                  'name': problem.name}]
                for result in dummy_results:
                    individual_result = fitbm_result.FittingResult(
                        **result)
                    results_problem.append(individual_result)
                new_minimizer_list.append(minimizer)
                LOGGER.warning(str(excp))

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
                    # Multi fit
                    # (will raise TypeError if these are not iterable)
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
    cost_func = controller.cost_func
    problem = controller.problem
    minimizer = controller.minimizer
    num_runs = options.num_runs
    has_jacobian, invalid_jacobians = controller.jacobian_information()
    jacobian_list = options.jac_method
    minimizer_name = minimizer
    results = []
    chi_sq = []
    new_minimizer_list = []
    minimizer_check = has_jacobian and minimizer not in invalid_jacobians
    try:
        for jac_method in jacobian_list:

            # Creates Jacobian class
            jacobian_cls = create_jacobian(jac_method)
            try:
                jacobian = jacobian_cls(cost_func)
            except NoJacobianError as excp:
                LOGGER.warning(str(excp))
                jacobian = False
            
            if jacobian:
                for num_method in options.num_method[jac_method]:
                    if minimizer_check:
                        num_method_str = ''
                        if jac_method != "analytic":
                            num_method_str = ' ' + num_method
                        LOGGER.info("                Jacobian: %s%s",
                                    jac_method, num_method_str)
                        minimizer_name = "{}: {}{}".format(
                            minimizer, jac_method, num_method_str)

                    jacobian.method = num_method

                    controller.jacobian = jacobian
                    try:
                        with grabbed_output:
                            # Calls timeit repeat with repeat = num_runs and
                            # number = 1
                            runtime_list = timeit.Timer(
                                setup=controller.prepare,
                                stmt=controller.fit
                            ).repeat(num_runs, 1)

                            runtime = sum(runtime_list) / num_runs
                            controller.cleanup()
                            controller.check_attributes()
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

                        chi_sq_check = any(np.isnan(n) for n in chi_sq) \
                            if problem.multifit else np.isnan(chi_sq)
                        if np.isnan(runtime) or chi_sq_check:
                            raise ControllerAttributeError(
                                "Either the computed runtime or chi_sq values "
                                "was a NaN.")
                    # Catching all exceptions as this means runtime cannot be
                    # calculated
                    # pylint: disable=broad-except
                    except Exception as excp:
                        LOGGER.warning(str(excp))

                        runtime = np.inf
                        controller.flag = 3
                        controller.final_params = \
                            None if not problem.multifit \
                            else [None] * len(controller.data_x)

                        chi_sq = np.inf if not problem.multifit \
                            else [np.inf] * len(controller.data_x)

                    # If bounds have been set, check that they have
                    # been respected by the minimizer and set error
                    # flag if not
                    if controller.problem.value_ranges is not None \
                            and controller.flag != 3:
                        controller.check_bounds_respected()

                    result_args = {'options': options,
                                   'cost_func': cost_func,
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

                    # For minimizers that do not accept jacobians we raise an
                    # StopIteration exception to exit the loop through the
                    # Jacobians
                    if not minimizer_check:
                        raise StopIteration
    except StopIteration:
        pass

    return results, chi_sq, new_minimizer_list
