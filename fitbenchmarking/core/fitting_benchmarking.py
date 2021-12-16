"""
Main module of the tool, this holds the master function that calls
lower level functions to fit and benchmark a set of problems
for a certain fitting software.
"""

from __future__ import absolute_import, division, print_function

import os
import timeit
import warnings

import numpy as np
from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.hessian.hessian_factory import create_hessian
from fitbenchmarking.jacobian.jacobian_factory import create_jacobian
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import fitbm_result, misc, output_grabber
from fitbenchmarking.utils.exceptions import (ControllerAttributeError,
                                              FitBenchmarkException,
                                              IncompatibleMinimizerError,
                                              MaxRuntimeError, NoHessianError,
                                              NoJacobianError,
                                              UnknownMinimizerError,
                                              UnsupportedMinimizerError,
                                              ValidationException)
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
                            loop_over_hessians()

    :param options: dictionary containing software used in fitting
                    the problem, list of minimizers and location of
                    json file contain minimizers
    :type options: fitbenchmarking.utils.options.Options
    :param data_dir: full path of a directory that holds a group of problem
                     definition files
    :type date_dir: str

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
        loop_over_benchmark_problems(problem_group, options)

    return results, failed_problems, unselected_minimizers


def loop_over_benchmark_problems(problem_group, options):
    """
    Loops over benchmark problems

    :param problem_group: locations of the benchmark problem files
    :type problem_group: list
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options

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
    for i, (fname, problem) in enumerate(problems):
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
            loop_over_starting_values(
                problem, options, grabbed_output)
        results.extend(problem_results)
        failed_problems.extend(problem_fails)

    return results, failed_problems, unselected_minimizers


def loop_over_starting_values(problem, options, grabbed_output):
    """
    Loops over starting values from the fitting problem.

    :param problem: The problem to benchmark on
    :type problem: fitbenchmarking.parsing.fitting_problem.FittingProblem
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third party output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

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
    for index in range(num_start_vals):
        LOGGER.info("    Starting value: %i/%i", index + 1, num_start_vals)
        if num_start_vals > 1:
            problem.name = name + ', Start {}'.format(index + 1)

        #############################
        # Loops over cost functions #
        #############################
        individual_problem_results, unselected_minimizers = \
            loop_over_cost_function(problem=problem,
                                    options=options,
                                    start_values_index=index,
                                    grabbed_output=grabbed_output)

        # Checks to see if all of the minimizers from every software raised an
        # exception and record the problem name if that is the case
        software_check = [np.isinf(v.chi_sq)
                          for v in individual_problem_results]
        if all(software_check):
            problem_fails.append(problem.name)
        problem_results.extend(individual_problem_results)

        # Reset name for next loop
        problem.name = name

    return (problem_results, problem_fails,
            unselected_minimizers)


def loop_over_cost_function(problem, options, start_values_index,
                            grabbed_output):
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

    :return: all results, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            dict[str, list[str]]
    """
    problem_results = []
    for cf in options.cost_func_type:
        cost_func_cls = create_cost_func(cf)
        cost_func = cost_func_cls(problem)
        #######################
        # Loops over software #
        #######################
        individual_problem_results, unselected_minimizers = \
            loop_over_fitting_software(cost_func=cost_func,
                                       options=options,
                                       start_values_index=start_values_index,
                                       grabbed_output=grabbed_output)
        problem_results.extend(individual_problem_results)

    return problem_results, unselected_minimizers


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
        problem_result, minimizer_failed = \
            loop_over_minimizers(controller=controller,
                                 minimizers=minimizers,
                                 options=options,
                                 grabbed_output=grabbed_output)

        unselected_minimizers[s] = minimizer_failed
        results.extend(problem_result)
    return results, unselected_minimizers


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

    :return: all results, and
             minimizers that were unselected due to algorithm_type
    :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
            list[str])
    """
    problem = controller.problem
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
                        options=options,
                        cost_func=controller.cost_func,
                        jac=None,
                        hess=None,
                        chi_sq=np.inf,
                        runtime=np.inf,
                        software=controller.software,
                        minimizer=minimizer,
                        algorithm_type=controller.record_alg_type(
                           minimizer, options.algorithm_type),
                        initial_params=controller.initial_params,
                        params=None,
                        error_flag=controller.flag,
                        name=problem.name)
                    results_problem.append(dummy_result)
                    LOGGER.warning(str(excp))

        if minimizer_check:
            ########################
            # Loops over Jacobians #
            ########################
            results = loop_over_jacobians(controller, options, grabbed_output)
            results_problem.extend(results)

    return results_problem, minimizer_failed


def loop_over_jacobians(controller, options, grabbed_output):
    """
    Loops over Jacobians set from the options file

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

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
                                                options,
                                                grabbed_output)

                results.extend(new_result)
                # For minimizers that do not accept jacobians we raise an
                # StopIteration exception to exit the loop through the
                # Jacobians
                if not minimizer_check:
                    raise StopIteration
    except StopIteration:
        pass

    return results


def loop_over_hessians(controller, options, grabbed_output):
    """
    Loops over Hessians set from the options file

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param options: FitBenchmarking options for current run
    :type options: fitbenchmarking.utils.options.Options
    :param grabbed_output: Object that removes third part output from console
    :type grabbed_output: fitbenchmarking.utils.output_grabber.OutputGrabber

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
            chi_sq, runtime = perform_fit(controller, options, grabbed_output)

            jac_str = cost_func.jacobian.name() \
                if minimizer in controller.jacobian_enabled_solvers else None
            hess_str = cost_func.hessian.name() \
                if cost_func.hessian is not None \
                and minimizer in controller.hessian_enabled_solvers \
                else None
            result_args = {'options': options,
                           'cost_func': cost_func,
                           'jac': jac_str,
                           'hess': hess_str,
                           'chi_sq': chi_sq,
                           'runtime': runtime,
                           'software': controller.software,
                           'minimizer': minimizer,
                           'algorithm_type': controller.record_alg_type(
                               minimizer, options.algorithm_type),
                           'initial_params': controller.initial_params,
                           'params': controller.final_params,
                           'error_flag': controller.flag,
                           'name': problem.name}
            if problem.multifit:
                # for multifit problems, multiple chi_sq values are stored
                # in a list i.e. we have multiple results
                for i in range(len(chi_sq)):
                    result_args.update(
                        {'dataset_id': i,
                         'name': f'{problem.name}, Dataset {i + 1}'})
                    new_result.append(
                        fitbm_result.FittingResult(**result_args))
            else:
                new_result.append(fitbm_result.FittingResult(**result_args))

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
    :return: The chi squared and runtime of the fit.
    :rtype: tuple(float, float)
    """
    num_runs = options.num_runs
    try:
        with grabbed_output:
            controller.validate()
            # Calls timeit repeat with repeat = num_runs and
            # number = 1
            runtime_list = timeit.Timer(
                setup=controller.prepare,
                stmt=controller.execute
            ).repeat(num_runs, 1)

            runtime = sum(runtime_list) / num_runs
            controller.cleanup()
            controller.check_attributes()
        min_time = np.min(runtime_list)
        ratio = np.max(runtime_list) / min_time
        tol = 4
        if ratio > tol:
            warnings.warn(
                'The ratio of the max time to the min is {0},'
                ' which is larger than the tolerance of {1}.'
                ' The min time is {2}. This can indicate that'
                ' the fitting engine is caching results. If the'
                ' min time is small this may just indicate that'
                ' other non-FitBenchmarking CPU activities are'
                ' taking place that affects the timing'
                ' results'.format(ratio, tol, min_time))
        chi_sq = controller.eval_chisq(
            params=controller.final_params,
            x=controller.data_x,
            y=controller.data_y,
            e=controller.data_e)

        chi_sq_check = any(np.isnan(n) for n in chi_sq) \
            if controller.problem.multifit else np.isnan(chi_sq)
        if np.isnan(runtime) or chi_sq_check:
            raise ControllerAttributeError(
                "Either the computed runtime or chi_sq values "
                "was a NaN.")
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

    controller.timer.reset()

    if controller.flag in [3, 6, 7]:
        # If there was an exception, set the runtime and
        # cost function value to be infinite
        runtime = np.inf
        multi_fit = controller.problem.multifit
        controller.final_params = \
            None if not multi_fit \
            else [None] * len(controller.data_x)

        chi_sq = np.inf if not multi_fit \
            else [np.inf] * len(controller.data_x)
    elif controller.problem.value_ranges is not None:
        # If bounds have been set, check that they have
        # been respected by the minimizer and set error
        # flag if not
        controller.check_bounds_respected()

    return chi_sq, runtime
