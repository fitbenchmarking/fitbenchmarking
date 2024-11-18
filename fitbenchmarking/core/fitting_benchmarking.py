"""
Main module of the tool, this holds the Fit Class that calls
methods to fit and benchmark a set of problems for a certain
fitting software.
"""

import os
import timeit

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
from fitbenchmarking.utils.exceptions import (
    ControllerAttributeError,
    FitBenchmarkException,
    IncompatibleCostFunctionError,
    IncompatibleMinimizerError,
    MaxRuntimeError,
    NoHessianError,
    NoJacobianError,
    UnknownMinimizerError,
    UnsupportedMinimizerError,
    ValidationException,
)
from fitbenchmarking.utils.log import get_logger

LOGGER = get_logger()


class Fit:
    """
    The class that performs the fit benchmark
    and collates the results.
    """

    def __init__(self, options, data_dir, checkpointer, label="benchmark"):
        """
        Initializes the Fit(ting) class.

        :param options: dictionary containing software used in fitting
                        the problem, list of minimizers and location of
                        json file contain minimizers
        :type options: fitbenchmarking.utils.options.Options
        :param data_dir: full path of a directory that holds a group of problem
                         definition files
        :type date_dir: str
        :param checkpointer: The object to use to save results as they're
                             generated
        :type checkpointer: Checkpoint
        :param label: The name for the dataset in the checkpoint
        :type label: str
        """
        self._options = options
        self._data_dir = data_dir
        self._checkpointer = checkpointer
        self._label = label
        self._results = []
        self._failed_problems = []
        self._unselected_minimizers = {}
        self.__start_values_index = 0
        self.__grabbed_output = output_grabber.OutputGrabber(self._options)
        self.__emissions_tracker = None
        self.__logger_prefix = "    "
        if "energy_usage" in options.table_type:
            self.__emissions_tracker = EmissionsTracker(measure_power_secs=1)

    def benchmark(self):
        """
        Call benchmarking on user input and list of paths.
        The benchmarking structure is:

        .. code-block:: python

            __loop_over_starting_values()
                __loop_over_software()
                    __loop_over_minimizers()
                        __loop_over_jacobians()
                            __loop_over_hessians()
                                __perform_fit()

        :return: all results,
                 problems where all fitting failed, and
                 minimizers that were unselected due to algorithm_type
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
                list[str],
                dict[str, list[str]]
        """
        problem_group = misc.get_problem_files(self._data_dir)

        problems, name_count = [], {}

        LOGGER.info("Parsing problems")
        for p in problem_group:
            try:
                with self.__grabbed_output:
                    parsed = parse_problem_file(p, self._options)
                    parsed.correct_data()
            except FitBenchmarkException as e:
                LOGGER.info("Could not parse problem from: %s", p)
                LOGGER.warning(e)
            else:
                name_count[parsed.name] = name_count.get(parsed.name, 0) + 1
                problems.append((p, parsed))

        LOGGER.info("Running problems")

        benchmark_pbar = (
            tqdm(
                problems,
                colour="green",
                desc="Benchmark problems",
                unit="Benchmark problem",
                leave=True,
            )
            if self._options.pbar
            else problems
        )

        name_index = {key: 0 for key in name_count}

        with logging_redirect_tqdm(loggers=[LOGGER]):
            for i, (fname, problem) in enumerate(benchmark_pbar):
                # Make the name unique
                if name_count[problem.name] > 1:
                    name_index[problem.name] += 1
                    problem.name += f" {name_index[problem.name]}"

                info_str = (
                    f" Running data from: {os.path.basename(fname)}"
                    f" {i + 1}/{len(problem_group)} "
                )
                LOGGER.info("\n%s", "#" * len(info_str))
                LOGGER.info(info_str)
                LOGGER.info("#" * len(info_str))

                results = self.__loop_over_starting_values(problem)
                self._results.extend(results)

                if self.__emissions_tracker:
                    _ = self.__emissions_tracker.stop()

        self._checkpointer.finalise_group(
            self._label, self._failed_problems, self._unselected_minimizers
        )

        return (
            self._results,
            self._failed_problems,
            self._unselected_minimizers,
        )

    def __loop_over_starting_values(self, problem):
        """
        Loops over starting values from the fitting problem.

        :param problem: The problem to benchmark on
        :type problem: fitbenchmarking.parsing.fitting_problem.FittingProblem

        :return: all results
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult]
        """
        name = problem.name
        num_start_vals = len(problem.starting_values)
        results = []

        num_start_vals_pbar = (
            trange(
                num_start_vals,
                colour="blue",
                leave=False,
                desc="Starting values   ",
                unit="Starting value   ",
            )
            if num_start_vals > 1 and self._options.pbar
            else range(num_start_vals)
        )

        for index in num_start_vals_pbar:
            LOGGER.info(
                "%sStarting value: %i/%i",
                self.__logger_prefix,
                index + 1,
                num_start_vals,
            )

            # Set the values of the start index
            self.__start_values_index = index

            if num_start_vals > 1:
                problem.name = f"{name}, Start {index + 1}"

            #############################
            # Loops over cost functions #
            #############################
            result = self.__loop_over_cost_function(problem)
            results.extend(result)

            # Checks to see if all of the minimizers from every software raised
            # an exception and record the problem name if that is the case
            software_check = [np.isinf(v.accuracy) for v in results]
            if all(software_check):
                self._failed_problems.append(problem.name)

            # Reset name for next loop
            problem.name = name

        return results

    def __loop_over_cost_function(self, problem):
        """
        Run benchmarking for each cost function given in options.

        :param problem: The problem to run fitting on
        :type problem: fitbenchmarking.parsing.fitting_problem.FittingProblem

        :return: all results
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult]
        """
        results = []
        for cf in self._options.cost_func_type:
            LOGGER.info("%sCost Function: %s", self.__logger_prefix * 2, cf)
            cost_func_cls = create_cost_func(cf)
            cost_func = cost_func_cls(problem)
            try:
                cost_func.validate_problem()
            except IncompatibleCostFunctionError:
                LOGGER.info(
                    "Problem is not compatible with this cost function (%s)",
                    cf,
                )
                continue
            #######################
            # Loops over software #
            #######################
            result = self.__loop_over_fitting_software(cost_func)
            results.extend(result)

        return results

    def __loop_over_fitting_software(self, cost_func):
        """
        Loops over fitting software selected in the options

        :param cost_func: a cost_func object containing information used
                          in fitting
        :type cost_func: CostFunction

        :return: all results
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult]
        """
        software = (
            self._options.software
            if isinstance(self._options.software, list)
            else [self._options.software]
        )
        results = []

        software_pbar = (
            tqdm(
                software,
                colour="yellow",
                desc="Software          ",
                unit="Software          ",
                leave=False,
            )
            if len(software) >= 3
            else software
        )

        for s in software_pbar:
            LOGGER.info("%sSoftware: %s", self.__logger_prefix * 3, s.upper())
            try:
                minimizers = self._options.minimizers[s]
            except KeyError as e:
                raise UnsupportedMinimizerError(
                    f"No minimizer given for software: {s}"
                ) from e
            with self.__grabbed_output:
                controller_cls = ControllerFactory.create_controller(
                    software=s
                )
                controller = controller_cls(cost_func=cost_func)

            controller.parameter_set = self.__start_values_index

            #########################
            # Loops over minimizers #
            #########################
            result, minimizer_failed = self.__loop_over_minimizers(
                controller=controller, minimizers=minimizers
            )
            results.extend(result)

            self._unselected_minimizers[s] = minimizer_failed

        return results

    def __loop_over_minimizers(self, controller, minimizers):
        """
        Loops over minimizers in fitting software

        :param controller: The software controller for the fitting
        :type controller: Object derived from BaseSoftwareController
        :param minimizers: array of minimizers used in fitting
        :type minimizers: list

        :return: all results, and
                 minimizers that were unselected due to algorithm_type
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
                list[str])
        """
        algorithm_type = self._options.algorithm_type
        minimizer_failed, results = [], []

        for minimizer in minimizers:
            controller.minimizer = minimizer
            minimizer_check = True
            LOGGER.info("%sMinimizer: %s", self.__logger_prefix * 4, minimizer)
            try:
                controller.validate_minimizer(minimizer, algorithm_type)
            except UnknownMinimizerError as excp:
                minimizer_failed.append(minimizer)
                minimizer_check = False
                LOGGER.warning(str(excp))

            try:
                controller.cost_func.validate_algorithm_type(
                    controller.algorithm_check, minimizer
                )
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

                        # Calling prepare to fill in the initial parameters
                        controller.prepare(skip_setup=True)
                        dummy_result = fitbm_result.FittingResult(
                            controller=controller
                        )
                        self._checkpointer.add_result(dummy_result)
                        results.append(dummy_result)
                        LOGGER.warning(str(excp))

            if minimizer_check:
                ########################
                # Loops over Jacobians #
                ########################
                result = self.__loop_over_jacobians(controller)
                results.extend(result)

        return results, minimizer_failed

    def __loop_over_jacobians(self, controller):
        """
        Loops over Jacobians set from the options file

        :param controller: The software controller for the fitting
        :type controller: Object derived from BaseSoftwareController

        :return: a FittingResult for each run.
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult]
        """
        cost_func = controller.cost_func
        minimizer = controller.minimizer
        jacobian_list = self._options.jac_method
        minimizer_check = minimizer in controller.jacobian_enabled_solvers
        sparsity_check = minimizer in controller.sparsity_enabled_solvers
        results = []
        try:
            for jac_method in jacobian_list:
                # Creates Jacobian class
                jacobian_cls = create_jacobian(jac_method)
                try:
                    jacobian = jacobian_cls(cost_func.problem)
                except NoJacobianError as excp:
                    LOGGER.warning(str(excp))
                    if jac_method == "analytic":
                        LOGGER.info("Using Scipy instead for jacobian")
                        jac_method = "scipy"
                        jacobian_cls = create_jacobian(jac_method)
                        jacobian = jacobian_cls(cost_func.problem)
                    else:
                        continue

                for num_method in self._options.jac_num_method[jac_method]:
                    jacobian.method = num_method
                    cost_func.jacobian = jacobian
                    if num_method.endswith("_sparse") and not sparsity_check:
                        continue
                    if minimizer_check:
                        LOGGER.info(
                            "%sJacobian: %s",
                            self.__logger_prefix * 5,
                            jacobian.name() if jacobian.name() else "default",
                        )

                    #######################
                    # Loops over Hessians #
                    #######################
                    result = self.__loop_over_hessians(controller)
                    results.extend(result)

                    # For minimizers that do not accept jacobians we raise an
                    # StopIteration exception to exit the loop through the
                    # Jacobians
                    if not minimizer_check:
                        raise StopIteration

        except StopIteration:
            pass

        return results

    def __loop_over_hessians(self, controller):
        """
        Loops over Hessians set from the options file

        :param controller: The software controller for the fitting
        :type controller: Object derived from BaseSoftwareController

        :return: a FittingResult for each run
        :rtype: list[fibenchmarking.utils.fitbm_result.FittingResult],
        """
        minimizer = controller.minimizer
        cost_func = controller.cost_func
        problem = controller.problem
        minimizer_check = minimizer in controller.hessian_enabled_solvers
        hessian_list = self._options.hes_method
        results = []

        # loop over selected hessian methods
        for hes_method in hessian_list:
            # if user has selected to use hessian info
            # then create hessian if minimizer accepts it
            if minimizer_check and hes_method != "default":
                hessian_cls = create_hessian(hes_method)
                try:
                    hessian = hessian_cls(
                        cost_func.problem, jacobian=cost_func.jacobian
                    )
                    cost_func.hessian = hessian
                except NoHessianError as excp:
                    LOGGER.warning(str(excp))
                    if hes_method == "analytic":
                        LOGGER.info("Using default method instead for hessian")
                        hes_method = "default"
                        cost_func.hessian = None
                    else:
                        continue
            else:
                cost_func.hessian = None

            for num_method in self._options.hes_num_method[hes_method]:
                if minimizer_check:
                    hess_name = "default"
                    if cost_func.hessian is not None:
                        cost_func.hessian.method = num_method
                        hess_name = cost_func.hessian.name()
                    LOGGER.info(
                        "%sHessian: %s", self.__logger_prefix * 6, hess_name
                    )

                # Perform the fit a number of times specified by num_runs
                accuracy, runtimes, energy = self.__perform_fit(controller)
                result_args = {
                    "controller": controller,
                    "accuracy": accuracy,
                    "runtimes": runtimes,
                    "energy": energy,
                    "runtime_metric": self._options.runtime_metric,
                }
                if problem.multifit:
                    # for multifit problems, multiple accuracy values
                    # are stored in a list i.e. we have multiple results
                    for i in range(len(accuracy)):
                        result_args["dataset"] = i
                        result = fitbm_result.FittingResult(**result_args)
                        results.append(result)
                        self._checkpointer.add_result(result)
                else:
                    result = fitbm_result.FittingResult(**result_args)
                    results.append(result)
                    self._checkpointer.add_result(result)

                # For minimizers that do not accept hessians we raise an
                # StopIteration exception to exit the loop through the
                # Hessians
                if not minimizer_check:
                    break

        return results

    def __perform_fit(self, controller):
        """
        Performs a fit using the provided controller and its data. It
        will be run a number of times specified by num_runs.

        :param controller: The software controller for the fitting
        :type controller: Object derived from BaseSoftwareController

        :return: The chi squared, runtimes and energy usage of the fit.
        :rtype: tuple(float, list[float], float)
        """
        num_runs = self._options.num_runs
        energy = np.nan
        tracker = self.__emissions_tracker

        try:
            with self.__grabbed_output:
                controller.validate()
                controller.prepare()
                if tracker:
                    tracker.start_task()
                    runtimes = timeit.Timer(stmt=controller.execute).repeat(
                        num_runs, 1
                    )
                    energy = tracker.stop_task().energy_consumed / num_runs
                else:
                    runtimes = timeit.Timer(stmt=controller.execute).repeat(
                        num_runs, 1
                    )
                controller.cleanup()
                controller.check_attributes()
            min_time = np.min(runtimes)
            ratio = np.max(runtimes) / min_time
            tol = 4
            if ratio > tol:
                LOGGER.warning(
                    "The ratio of the max time to the min is %.8f,"
                    " which is larger than the tolerance of %d."
                    " The min time is %.8f. This can indicate that"
                    " the fitting engine is caching results. If the"
                    " min time is small this may just indicate that"
                    " other non-FitBenchmarking CPU activities are"
                    " taking place that affects the timing"
                    " results",
                    ratio,
                    tol,
                    min_time,
                )

            # Avoid deleting results (max runtime exception) if gotten this far
            controller.timer.reset()
            if controller.params_pdfs is None:
                accuracy = controller.eval_chisq(
                    params=controller.final_params,
                    x=controller.data_x,
                    y=controller.data_y,
                    e=controller.data_e,
                )
            else:
                conf = controller.eval_confidence()
                accuracy = 1 / conf if conf != 0 else np.inf

            accuracy_check = (
                any(np.isnan(n) for n in accuracy)
                if controller.problem.multifit
                else np.isnan(accuracy)
            )
            if np.isnan(runtimes).any() or accuracy_check:
                raise ControllerAttributeError(
                    "Either the computed runtime "
                    "or accuracy values were a NaN."
                )
        except ValidationException as ex:
            LOGGER.warning(str(ex))
            controller.flag = 7
        except Exception as ex:
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
        if hasattr(controller, "clear_matlab"):
            controller.clear_matlab()

        # Reset the controller timer once exceptions have been handled
        controller.timer.reset()

        # ensure emissions tracker has been stopped if energy not set
        if energy == np.nan and self.__emissions_tracker:
            _ = self.__emissions_tracker.stop_task()

        if controller.flag in [3, 6, 7]:
            # If there was an exception, set the runtimes and
            # cost function value to be infinite
            energy = np.inf
            multi_fit = controller.problem.multifit
            runtimes = [np.inf] * num_runs
            controller.final_params = (
                None if not multi_fit else [None] * len(controller.data_x)
            )

            accuracy = (
                np.inf if not multi_fit else [np.inf] * len(controller.data_x)
            )
        elif controller.problem.value_ranges is not None:
            # If bounds have been set, check that they have
            # been respected by the minimizer and set error
            # flag if not
            controller.check_bounds_respected()

        return accuracy, runtimes, energy
