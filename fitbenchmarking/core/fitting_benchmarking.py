"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

import os
import timeit
import warnings

from contextlib import nullcontext
import numpy as np
from codecarbon import EmissionsTracker
from tqdm import tqdm, trange
from tqdm.contrib.logging import logging_redirect_tqdm

from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.hessian.hessian_factory import create_hessian
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, misc, output_grabber
from fitbenchmarking.utils.exceptions import (ControllerAttributeError,
                                              FitBenchmarkException,
                                              IncompatibleCostFunctionError,
                                              IncompatibleMinimizerError,
                                              MaxRuntimeError, NoHessianError,
                                              NoJacobianError,
                                              UnknownMinimizerError,
                                              UnsupportedMinimizerError,
                                              ValidationException)
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def benchmark(options, data_dir, checkpointer, label='benchmark'):
    """
    Gather the user input and list of paths. Call benchmarking on these.
    The benchmarking structure is:

    .. code-block:: python

        loop_over_benchmark_problems()
            loop_over_starting_values()
                loop_over_software()
                    loop_over_minimizers()
                        loop_over_jacobians()
                            loop_over_hessians()

    :param options: dictionary containing software used in fitting
                    the problem, list of minimizers and location of
                    json file contain minimizers
    :type options: fitbenchmarking.utils.options.Options
    :param data_dir: full path of a directory that holds a group of problem
                     definition files
    :type date_dir: str
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint
    :param label: The name for the dataset in the checkpoint
    :type label: str

    :return: all results,
             problems where all fitting failed,
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            list[str],
            dict[str, list[str]]
    """

    # Extract problem definitions
    problem_group = misc.get_problem_files(data_dir)

    #################################
    # Loops over benchmark problems #
    #################################
    results, failed_problems, unselected_minimizers = \
        loop_over_benchmark_problems(problem_group,
                                     options=options,
                                     checkpointer=checkpointer)

    checkpointer.finalise_group(label=label,
                                failed_problems=failed_problems,
                                unselected_minimizers=unselected_minimizers)

    return results, failed_problems, unselected_minimizers


def loop_over_benchmark_problems(problem_group, options, checkpointer):
    """
    Loops over benchmark problems

    :param problem_group: locations of the benchmark problem files
    :type problem_group: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: all results,
             problems where all fitting failed, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            list[str],
            dict[str, list[str]]
    """
    grabbed_output = output_grabber.OutputGrabber(options)
    results = []
    failed_problems = []
    unselected_minimizers = []

    LOGGER.info('Parsing problems')
    problems = []
    name_count = {}  # Count the names so that we can give duplicates an id
    for i, p in enumerate(problem_group):
        try:
            with grabbed_output:
                parsed_problem = parse_problem_file(p, options)
                parsed_problem.correct_data()
        except FitBenchmarkException as e:
            LOGGER.info("Could not parse problem from: %s", p)
            LOGGER.warning(e)
        else:
            name = parsed_problem.name
            name_count[name] = name_count.get(name, 0) + 1
            problems.append((p, parsed_problem))

    name_index = {key: 0 for key in name_count}
    LOGGER.info('Running problems')

    if options.pbar:
        benchmark_pbar = tqdm(problems, colour='green',
                              desc="Benchmark problems",
                              unit="Benchmark problem", leave=True)
    else:
        benchmark_pbar = problems

    with logging_redirect_tqdm(loggers=[LOGGER]):
        for i, (fname, problem) in enumerate(benchmark_pbar):
            # Make the name unique
            if name_count[problem.name] > 1:
                name_index[problem.name] += 1
                problem.name += f' {name_index[problem.name]}'

            info_str = f" Running data from: {os.path.basename(fname)} " + \
                       f"{i + 1}/{len(problem_group)}"
            LOGGER.info('\n%s', '#' * (len(info_str) + 1))
            LOGGER.info(info_str)
            LOGGER.info('#' * (len(info_str) + 1))

            ##############################
            # Loops over starting values #
            ##############################
            problem_results, problem_fails, \
                unselected_minimizers = \
                loop_over_starting_values(problem,
                                          options=options,
                                          grabbed_output=grabbed_output,
                                          checkpointer=checkpointer)
            results.extend(problem_results)
            failed_problems.extend(problem_fails)

    return results, failed_problems, unselected_minimizers


def loop_over_starting_values(problem, options, grabbed_output, checkpointer):
    """
    Loops over starting values from the fitting problem.

    :param problem: The problem to benchmark on
    :type problem: fitbenchmarking.parsing.fitting_problem.FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third party output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: all results,
             problems where all fitting failed, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            list[str],
            dict[str, list[str]]
    """
    problem_fails = []
    name = problem.name
    num_start_vals = len(problem.starting_values)
    problem_results = []
    unselected_minimizers = {}

    if num_start_vals >= 2 and options.pbar:
        num_start_vals_pbar = trange(num_start_vals, colour='blue',
                                     leave=False, desc="Starting values   ",
                                     unit="Starting value   ")
    else:
        num_start_vals_pbar = range(num_start_vals)

    for index in num_start_vals_pbar:
        LOGGER.info("    Starting value: %i/%i", index + 1, num_start_vals)
        if num_start_vals > 1:
            problem.name = f'{name}, Start {index + 1}'

        #############################
        # Loops over cost functions #
        #############################
        individual_problem_results, unselected_minimizers = \
            loop_over_cost_function(problem=problem,
                                    options=options,
                                    start_values_index=index,
                                    grabbed_output=grabbed_output,
                                    checkpointer=checkpointer)

        # Checks to see if all of the minimizers from every software raised an
        # exception and record the problem name if that is the case
        software_check = [np.isinf(v.accuracy)
                          for v in individual_problem_results]
        if all(software_check):
            problem_fails.append(problem.name)
        problem_results.extend(individual_problem_results)

        # Reset name for next loop
        problem.name = name

    return problem_results, problem_fails, unselected_minimizers


def loop_over_cost_function(problem, options, start_values_index,
                            grabbed_output, checkpointer):
    """
    Run benchmarking for each cost function given in options.

    :param problem: The problem to run fitting on
    :type problem: fitbenchmarking.parsing.fitting_problem.FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param start_values_index: Integer that selects the starting values when
                               datasets have multiple ones.
    :type start_values_index: int
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: all results, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            dict[str, list[str]]
    """
    unselected_minimizers = {}
    problem_results = []
    for cf in options.cost_func_type:
        cost_func_cls = create_cost_func(cf)
        cost_func = cost_func_cls(problem)
        try:
            cost_func.validate_problem()
        except IncompatibleCostFunctionError:
            LOGGER.info(
                'Problem is not compatible with this cost function (%s)', cf)
            continue
        #######################
        # Loops over software #
        #######################
        individual_problem_results, unselected_minimizers = \
            loop_over_fitting_software(cost_func=cost_func,
                                       options=options,
                                       start_values_index=start_values_index,
                                       grabbed_output=grabbed_output,
                                       checkpointer=checkpointer)
        problem_results.extend(individual_problem_results)

    return problem_results, unselected_minimizers


def loop_over_fitting_software(cost_func, options, start_values_index,
                               grabbed_output, checkpointer):
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
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: all results, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            dict[str, list[str]]
    """
    results = []
    software = options.software
    if not isinstance(software, list):
        software = [software]

    unselected_minimizers = {}

    if len(software) >= 3:
        software_pbar = tqdm(software, colour='yellow',
                             desc="Software          ",
                             unit="Software          ", leave=False)
    else:
        software_pbar = software

    for s in software_pbar:
        LOGGER.info("        Software: %s", s.upper())
        try:
            minimizers = options.minimizers[s]
        except KeyError as e:
            raise UnsupportedMinimizerError(
                f'No minimizer given for software: {s}') from e
        with grabbed_output:
            controller_cls = ControllerFactory.create_controller(
                software=s)
            controller = controller_cls(cost_func=cost_func)

        controller.parameter_set = start_values_index

        #########################
        # Loops over minimizers #
        #########################
        problem_result, minimizer_failed = \
            loop_over_minimizers(controller=controller,
                                 minimizers=minimizers,
                                 options=options,
                                 grabbed_output=grabbed_output,
                                 checkpointer=checkpointer)

        unselected_minimizers[s] = minimizer_failed
        results.extend(problem_result)
    return results, unselected_minimizers


def loop_over_minimizers(controller, minimizers, options, grabbed_output,
                         checkpointer):
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
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: all results, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            list[str])
    """
    algorithm_type = options.algorithm_type

    results_problem = []
    minimizer_failed = []
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
                if minimizer_check:
                    minimizer_check = False
                    controller.flag = 4
                    dummy_result = fitbm_result.FittingResult(
                        controller=controller)
                    checkpointer.add_result(dummy_result)
                    results_problem.append(dummy_result)
                    LOGGER.warning(str(excp))

        if minimizer_check:
            ########################
            # Loops over Jacobians #
            ########################
            results = loop_over_jacobians(controller,
                                          options=options,
                                          grabbed_output=grabbed_output,
                                          checkpointer=checkpointer)
            results_problem.extend(results)

    return results_problem, minimizer_failed


def loop_over_jacobians(controller, options, grabbed_output, checkpointer):
    """
    Loops over Jacobians set from the options file

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: a FittingResult for each run.
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult]
    """
    cost_func = controller.cost_func
    minimizer = controller.minimizer
    jacobian_list = options.jac_method
    results = []
    minimizer_check = minimizer in controller.jacobian_enabled_solvers
    try:
        for jac_method in jacobian_list:

            # Creates Jacobian class
            jacobian_cls = create_jacobian(jac_method)
            try:
                jacobian = jacobian_cls(cost_func.problem)
            except NoJacobianError as excp:
                LOGGER.warning(str(excp))
                continue

            for num_method in options.jac_num_method[jac_method]:
                jacobian.method = num_method
                cost_func.jacobian = jacobian
                if minimizer_check:
                    LOGGER.info(
                        "                Jacobian: %s",
                        jacobian.name() if jacobian.name() else "default"
                    )

                #######################
                # Loops over Hessians #
                #######################
                new_result = loop_over_hessians(controller,
                                                options=options,
                                                grabbed_output=grabbed_output,
                                                checkpointer=checkpointer)

                results.extend(new_result)
                # For minimizers that do not accept jacobians we raise an
                # StopIteration exception to exit the loop through the
                # Jacobians
                if not minimizer_check:
                    raise StopIteration
    except StopIteration:
        pass

    return results


def loop_over_hessians(controller, options, grabbed_output, checkpointer):
    """
    Loops over Hessians set from the options file

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber
    :param checkpointer: The object to use to save results as they're generated
    :type checkpointer: Checkpoint

    :return: a FittingResult for each run
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
    """
    minimizer = controller.minimizer
    cost_func = controller.cost_func
    problem = controller.problem
    minimizer_check = minimizer in controller.hessian_enabled_solvers
    hessian_list = options.hes_method
    new_result = []

    # loop over selected hessian methods
    for hes_method in hessian_list:
        # if user has selected to use hessian info
        # then create hessian if minimizer accepts it
        if minimizer_check and hes_method != 'default':
            hessian_cls = create_hessian(hes_method)
            try:
                hessian = hessian_cls(cost_func.problem,
                                      jacobian=cost_func.jacobian)
                cost_func.hessian = hessian
            except NoHessianError as excp:
                LOGGER.warning(str(excp))
                continue
        else:
            cost_func.hessian = None

        for num_method in options.hes_num_method[hes_method]:
            if minimizer_check:
                hess_name = "default"
                if cost_func.hessian is not None:
                    cost_func.hessian.method = num_method
                    hess_name = cost_func.hessian.name()
                LOGGER.info("                   Hessian: %s",
                            hess_name)

            # Perform the fit a number of times specified by num_runs
            accuracy, runtimes, emissions = perform_fit(
                controller, options, grabbed_output)
            result_args = {'controller': controller,
                           'accuracy': accuracy,
                           'runtimes': runtimes,
                           'emissions': emissions}
            if problem.multifit:
                # for multifit problems, multiple accuracy values are stored
                # in a list i.e. we have multiple results
                for i in range(len(accuracy)):
                    result_args['dataset'] = i
                    result = fitbm_result.FittingResult(**result_args)
                    new_result.append(result)
                    checkpointer.add_result(result)
            else:
                result = fitbm_result.FittingResult(**result_args)
                new_result.append(result)
                checkpointer.add_result(result)

            # For minimizers that do not accept hessians we raise an
            # StopIteration exception to exit the loop through the
            # Hessians
            if not minimizer_check:
                break

    return new_result


def perform_fit(controller, options, grabbed_output):
    """
    Performs a fit using the provided controller and its data. It
    will be run a number of times specified by num_runs.

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: The user options for the benchmark.
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber
    :return: The chi squared, runtimes and emissions of the fit.
    :rtype: tuple(float, list[float], float)
    """
    num_runs = options.num_runs

    track_emissions = 'emissions' in options.table_type
    if track_emissions:
        emissions_tracker = EmissionsTracker()
    else:
        emissions_tracker = nullcontext()
    emissions = np.inf
    try:
        with grabbed_output:
            controller.validate()
            controller.prepare()
            with emissions_tracker:
                # Calls timeit repeat with repeat = num_runs and number = 1
                runtimes = timeit.Timer(
                    stmt=controller.execute
                ).repeat(num_runs, 1)
            if track_emissions:
                # stop emissions tracking after all runs have completed
                emissions = emissions_tracker.final_emissions / num_runs

            controller.cleanup()
            controller.check_attributes()
        min_time = np.min(runtimes)
        ratio = np.max(runtimes) / min_time
        tol = 4
        if ratio > tol:
            warnings.warn(
                f'The ratio of the max time to the min is {ratio},'
                f' which is larger than the tolerance of {tol}.'
                f' The min time is {min_time}. This can indicate that'
                ' the fitting engine is caching results. If the'
                ' min time is small this may just indicate that'
                ' other non-FitBenchmarking CPU activities are'
                ' taking place that affects the timing'
                ' results')

        # Avoid deleting results (max runtime exception) if gotten this far
        controller.timer.reset()
        if controller.params_pdfs is None:
            accuracy = controller.eval_chisq(params=controller.final_params,
                                             x=controller.data_x,
                                             y=controller.data_y,
                                             e=controller.data_e)
        else:
            accuracy = controller.eval_confidence()

        accuracy_check = any(np.isnan(n) for n in accuracy) \
            if controller.problem.multifit else np.isnan(accuracy)
        if np.isnan(runtimes).any() or accuracy_check:
            raise ControllerAttributeError(
                "Either the computed runtime or accuracy values were a NaN.")
    except ValidationException as ex:
        LOGGER.warning(str(ex))
        controller.flag = 7
    except Exception as ex:  # pylint: disable=broad-except
        LOGGER.warning(str(ex))

        # Note: Handle all exceptions as general exception to cover case
        #       where software re-raises our exception as a new type.
        error_flags = {MaxRuntimeError: 6}

        controller.flag = 3
        for error, flag in error_flags.items():
            if error.class_message in str(ex):
                controller.flag = flag
                break

    # If Using a matlab controller, release the memory in matlab
    if hasattr(controller, 'clear_matlab'):
        controller.clear_matlab()

    # Reset the controller timer once exceptions have been handled
    controller.timer.reset()

    if controller.flag in [3, 6, 7]:
        # If there was an exception, set the runtimes and
        # cost function value to be infinite
        emissions = np.inf
        multi_fit = controller.problem.multifit
        runtimes = [np.inf] * num_runs
        controller.final_params = \
            None if not multi_fit \
            else [None] * len(controller.data_x)

        accuracy = np.inf if not multi_fit \
            else [np.inf] * len(controller.data_x)
    elif controller.problem.value_ranges is not None:
        # If bounds have been set, check that they have
        # been respected by the minimizer and set error
        # flag if not
        controller.check_bounds_respected()
    return accuracy, runtimes, emissions
