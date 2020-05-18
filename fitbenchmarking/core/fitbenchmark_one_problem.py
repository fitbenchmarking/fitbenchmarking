"""
Fit benchmark one problem functions.
"""

from __future__ import absolute_import, division, print_function

import timeit
import warnings

import numpy as np

from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.utils import fitbm_result, output_grabber
from fitbenchmarking.utils.exceptions import UnknownMinimizerError
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


def fitbm_one_prob(problem, options):
    """
    Sets up the controller for a particular problem and fits the models
    provided in the problem object.

    :param problem: a problem object containing information used in fitting
    :type problem: FittingProblem
    :param options: all the information specified by the user
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

    name = problem.name
    num_start_vals = len(problem.starting_values)
    problem_fails = []
    unselected_minimzers = {}
    for i in range(num_start_vals):
        LOGGER.info("    Starting value: {0}/{1}".format(i + 1,
                                                         num_start_vals))

        if num_start_vals > 1:
            problem.name = name + ', Start {}'.format(i + 1)
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

            controller.parameter_set = i
            problem_result, minimizer_failed = benchmark(controller=controller,
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
    # Reset problem.name
    problem.name = name
    return results, problem_fails, unselected_minimzers


def benchmark(controller, minimizers, options):
    """
    Fit benchmark one problem, with one function definition and all
    the selected minimizers, using the chosen fitting software.

    :param controller: The software controller for the fitting
    :type controller: Object derived from BaseSoftwareController
    :param minimizers: array of minimizers used in fitting
    :type minimizers: list
    :param options: all the information specified by the user
    :type options: fitbenchmarking.utils.options.Options

    :return: list of all results and dictionary of unselected minimizers
             based on algorithm_type
    :rtype: tuple(list of fibenchmarking.utils.fitbm_result.FittingResult,
                  dictionary of minimizers)
    """
    grabbed_output = output_grabber.OutputGrabber(options)
    problem = controller.problem

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
