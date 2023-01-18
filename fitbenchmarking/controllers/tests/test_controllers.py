# pylint: disable=too-many-lines
"""
Tests for the controllers available from a default fitbenchmarking install
"""
import inspect
import os
from unittest import TestCase

import numpy as np
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module

from conftest import run_for_test_types
from fitbenchmarking import test_files
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.jacobian.default_jacobian import Default
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from fitbenchmarking.hessian.scipy_hessian import Scipy as ScipyHessian
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options

if TEST_TYPE in ['default', 'all']:
    from fitbenchmarking.controllers.bumps_controller import BumpsController
    from fitbenchmarking.controllers.controller_factory import \
        ControllerFactory
    from fitbenchmarking.controllers.dfo_controller import DFOController
    from fitbenchmarking.controllers.minuit_controller import MinuitController
    from fitbenchmarking.controllers.scipy_controller import ScipyController
    from fitbenchmarking.controllers.scipy_go_controller import \
        ScipyGOController
    from fitbenchmarking.controllers.scipy_ls_controller import \
        ScipyLSController
<<<<<<< HEAD
    from fitbenchmarking.controllers.nlopt_controller import \
        NLoptController, nlopt
=======
    from fitbenchmarking.controllers.lmfit_controller import LmfitController
>>>>>>> master

if TEST_TYPE == 'all':
    from fitbenchmarking.controllers.gsl_controller import GSLController
    from fitbenchmarking.controllers.levmar_controller import LevmarController
    from fitbenchmarking.controllers.mantid_controller import MantidController
    from fitbenchmarking.controllers.ralfit_controller import RALFitController
    from fitbenchmarking.controllers.gradient_free_controller import\
        GradientFreeController
    from fitbenchmarking.controllers.gofit_controller import GOFitController
    from fitbenchmarking.controllers.ceres_controller import CeresController

if TEST_TYPE == 'matlab':
    from fitbenchmarking.controllers.matlab_controller import MatlabController
    from fitbenchmarking.controllers.matlab_opt_controller import\
        MatlabOptController
    from fitbenchmarking.controllers.matlab_stats_controller import\
        MatlabStatsController
    from fitbenchmarking.controllers.matlab_curve_controller import\
        MatlabCurveController
    from fitbenchmarking.controllers.horace_controller import\
        HoraceController


# pylint: disable=attribute-defined-outside-init, protected-access
def make_cost_func(file_name='cubic.dat'):
    """
    Helper function that returns a simple fitting problem
    """

    options = Options()

    bench_prob_dir = os.path.dirname(inspect.getfile(test_files))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    cost_func = WeightedNLLSCostFunc(fitting_problem)
    return cost_func


class DummyController(Controller):
    """
    Minimal instantiatable subclass of Controller class for testing
    """
    # pylint: disable=missing-function-docstring

    def setup(self):
        self.setup_result = 53

    def fit(self):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def error_flags(self):
        raise NotImplementedError
    # pylint: enable=missing-function-docstring


class ControllerSharedTesting:
    """
    Tests used by all controllers
    """

    @staticmethod
    def controller_run_test(controller):
        """
        Utility function to run controller and check output is in generic form

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.parameter_set = 0
        controller.prepare()
        controller.execute()
        controller.cleanup()

        assert len(controller.final_params) == len(controller.initial_params)

    @staticmethod
    def check_converged(controller):
        """
        Utility function to check controller.cleanup() produces a success flag

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.cleanup()
        assert controller.flag == 0

    @staticmethod
    def check_max_iterations(controller):
        """
        Utility function to check controller.cleanup() produces a maximum
        iteration flag

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.cleanup()
        assert controller.flag == 1

    @staticmethod
    def check_diverged(controller):
        """
        Utility function to check controller.cleanup() produces a fail

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.cleanup()
        assert controller.flag == 2


class BaseControllerTests(TestCase):
    """
    Tests for base software controller class methods.
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem

    def test_data(self):
        """
        BaseSoftwareController: Test data is read into controller correctly
        """

        controller = DummyController(self.cost_func)

        if self.problem.start_x is not None:
            assert min(controller.data_x) >= self.problem.start_x
        if self.problem.end_x is not None:
            assert max(controller.data_x) <= self.problem.end_x

        assert len(controller.data_e) == len(controller.data_x)
        assert len(controller.data_e) == len(controller.data_y)

        self.assertTrue(all(x in self.problem.data_x
                            for x in controller.data_x))
        self.assertTrue(all(y in self.problem.data_y
                            for y in controller.data_y))

        e_is_default = self.problem.data_e is None
        if not e_is_default:
            self.assertTrue(all(e in self.problem.data_e
                                for e in controller.data_e))

    def test_prepare(self):
        """
        BaseSoftwareController: Test prepare function
        """
        controller = DummyController(self.cost_func)
        controller.minimizer = 'test'
        controller.parameter_set = 0
        controller.prepare()
        assert controller.setup_result == 53

    def test_eval_chisq(self):
        """
        BaseSoftwareController: Test eval_chisq function
        """
        controller = DummyController(self.cost_func)

        params = np.array([1, 2, 3, 4])
        x = np.array([6, 2, 32, 4])
        y = np.array([1, 21, 3, 4])
        e = np.array([.5, .003, 1, 2])

        result = self.cost_func.eval_cost(params=params, x=x, y=y, e=e)

        assert controller.eval_chisq(params=params, x=x, y=y, e=e) == result

    def test_check_flag_attr(self):
        """
        BaseSoftwareController: Test check_attributes function for _flag
                                attribute
        """
        controller = DummyController(self.cost_func)
        with self.assertRaises(exceptions.ControllerAttributeError):
            controller.check_attributes()
        controller.flag = 1
        controller.final_params = [1]
        controller.check_attributes()

    def test_check_valid_flag(self):
        """
        BaseSoftwareController: Test flag setting with valid values
        """
        controller = DummyController(self.cost_func)
        controller.final_params = [1]

        for flag in [0, 1, 2, 3]:
            controller.flag = flag

    def test_check_invalid_flag(self):
        """
        BaseSoftwareController: Test flag setting with invalid values
        """
        controller = DummyController(self.cost_func)
        controller.final_params = [1, 2, 3, 4, 5]
        with self.assertRaises(exceptions.ControllerAttributeError):
            controller.flag = 10

    def test_check_final_params_attr(self):
        """
        BaseSoftwareController: Test check_attributes function for final_params
                                attribute
        """
        controller = DummyController(self.cost_func)
        controller.final_params = [1, 2, 3, 4, 5]
        controller.flag = 3
        controller.check_attributes()

    def test_check_invalid_final_params(self):
        """
        BaseSoftwareController: Test final_params setting with invalid values
        """
        controller = DummyController(self.cost_func)
        controller.flag = 1
        controller.final_params = [1, np.inf]
        with self.assertRaises(exceptions.ControllerAttributeError):
            controller.check_attributes()

    def test_validate_minimizer_true(self):
        """
        BaseSoftwareController: Test validate_minimizer with valid
                                minimizer
        """
        controller = DummyController(self.cost_func)
        controller.algorithm_check = {'all': ['min1', 'min2']}
        algorithm_type = ['all']
        minimizer = 'min1'
        controller.validate_minimizer(minimizer, algorithm_type)

    def test_validate_minimizer_false(self):
        """
        BaseSoftwareController: Test validate_minimizer with invalid
                                minimizer
        """
        controller = DummyController(self.cost_func)
        controller.algorithm_check = {'all': ['min1', 'min2']}
        algorithm_type = ['all']
        minimizer = 'min_unknown'
        with self.assertRaises(exceptions.UnknownMinimizerError):
            controller.validate_minimizer(minimizer, algorithm_type)

    def test_check_minimizer_bounds_true(self):
        """
        BaseSoftwareController: Test check_minimizer_bounds with
                                minimizer that supports bounds
        """
        controller = DummyController(self.cost_func)
        controller.support_for_bounds = True
        controller.no_bounds_minimizers = ['no_bounds_minimizer']
        minimizer = 'bounds_minimizer'
        controller.check_minimizer_bounds(minimizer)

    def test_check_minimizer_bounds_false(self):
        """
        BaseSoftwareController: Test check_minimizer_bounds with
                                minimizer that does not support bounds
        """
        controller = DummyController(self.cost_func)
        controller.support_for_bounds = True
        controller.no_bounds_minimizers = ['no_bounds_minimizer']
        minimizer = 'no_bounds_minimizer'
        with self.assertRaises(exceptions.IncompatibleMinimizerError):
            controller.check_minimizer_bounds(minimizer)

    def test_record_alg_type(self):
        """
        BaseSoftwareController: Test record_alg_type function
        """
        controller = DummyController(self.cost_func)
        controller.algorithm_check = {'all': ['min1', 'min2'],
                                      'general': ['min1']}
        algorithm_type = ['general']
        minimizer = 'min1'
        type_str = controller.record_alg_type(minimizer, algorithm_type)
        assert type_str == 'general'

    def test_bounds_respected_true(self):
        '''
        Test that correct error flag is set when
        final params respect specified parameter bounds
        '''
        controller = DummyController(self.cost_func)
        controller.value_ranges = [(10, 20), (20, 30)]
        controller.final_params = [15, 30]
        controller.flag = 0

        controller.check_bounds_respected()

        assert controller.flag == 0

    def test_bounds_respected_false(self):
        '''
        Test that correct error flag is set when
        final params do not respect specified parameter bounds
        '''
        controller = DummyController(self.cost_func)
        controller.value_ranges = [(10, 20), (20, 30)]
        controller.final_params = [25, 35]
        controller.flag = 0

        controller.check_bounds_respected()

        assert controller.flag == 5

    def test_software_property_default(self):
        '''
        Test that the software property works when no controller name is
        present
        '''
        controller = DummyController(self.cost_func)
        software = controller.software
        assert software == 'dummy'

    def test_software_property_with_cont_name(self):
        '''
        Test that the software property works when controller name is
        present
        '''
        controller = DummyController(self.cost_func)
        controller.controller_name = 'my_dummy_software'
        software = controller.software
        assert software == 'my_dummy_software'


@run_for_test_types(TEST_TYPE, 'default', 'all')
class DefaultControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = '2-point'
        self.cost_func.jacobian = self.jac
        self.shared_tests = ControllerSharedTesting()

    def test_bumps(self):
        """
        BumpsController: Test for output shape
        """
        controller = BumpsController(self.cost_func)
        controller.minimizer = 'amoeba'
        self.shared_tests.controller_run_test(controller)

        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 2
        self.shared_tests.check_max_iterations(controller)
        controller._status = 1
        self.shared_tests.check_diverged(controller)

    def test_dfo(self):
        """
        DFOController: Tests for output shape
        """
        controller = DFOController(self.cost_func)
        # test one from each class
        minimizers = ['dfogn',
                      'dfols']

        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 2
            self.shared_tests.check_max_iterations(controller)
            controller._status = 5
            self.shared_tests.check_diverged(controller)

    def test_minuit(self):
        """
        MinuitController: Tests for output shape
        """
        controller = MinuitController(self.cost_func)
        controller.minimizer = 'minuit'
        self.shared_tests.controller_run_test(controller)

        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 2
        self.shared_tests.check_diverged(controller)

    def test_scipy(self):
        """
        ScipyController: Test for output shape
        """
        controller = ScipyController(self.cost_func)
        controller.minimizer = 'CG'
        self.shared_tests.controller_run_test(controller)

        controller.result.success = True
        self.shared_tests.check_converged(controller)
        controller.result.success = False
        self.shared_tests.check_diverged(controller)
        controller.result.message = 'iteration limit reached'
        self.shared_tests.check_max_iterations(controller)

    def test_scipy_ls(self):
        """
        ScipyLSController: Test for output shape
        """
        controller = ScipyLSController(self.cost_func)
        controller.minimizer = 'lm'

        self.shared_tests.controller_run_test(controller)

        controller._status = 1
        self.shared_tests.check_converged(controller)
        controller._status = 0
        self.shared_tests.check_max_iterations(controller)
        controller._status = -1
        self.shared_tests.check_diverged(controller)

    def test_nlopt(self):
        """
        NLoptController: Test for output shape
        """
        controller = NLoptController(self.cost_func)
        controller.minimizer = 'LD_VAR2'

        self.shared_tests.controller_run_test(controller)

        controller._status = nlopt.SUCCESS
        self.shared_tests.check_converged(controller)
        controller._status = nlopt.XTOL_REACHED
        self.shared_tests.check_converged(controller)
        controller._status = nlopt.FTOL_REACHED
        self.shared_tests.check_converged(controller)
        controller._status = nlopt.MAXEVAL_REACHED
        self.shared_tests.check_max_iterations(controller)
        controller._status = -1
        self.shared_tests.check_diverged(controller)

    def test_lmfit(self):
        """
        LmfitController: Test for output shape
        """
        controller = LmfitController(self.cost_func)
        controller.minimizer = 'leastsq'
        self.shared_tests.controller_run_test(controller)

        controller.lmfit_out.success = True
        self.shared_tests.check_converged(controller)
        controller.lmfit_out.success = False
        self.shared_tests.check_diverged(controller)


@run_for_test_types(TEST_TYPE, 'all')
class ControllerBoundsTests(TestCase):
    """
    Tests to ensure controllers handle and respect bounds correctly
    """

    def setUp(self):
        """
        Setup for bounded problem
        """
        self.cost_func = make_cost_func('cubic-fba-test-bounds.txt')
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = '2-point'
        self.cost_func.jacobian = self.jac

    def check_bounds(self, controller):
        """
        Run bounded problem and check `final_params` respect
        parameter bounds
        """
        controller.parameter_set = 0
        controller.prepare()
        controller.fit()
        controller.cleanup()

        for count, value in enumerate(controller.final_params):
            self.assertLessEqual(controller.value_ranges[count][0], value)
            self.assertGreaterEqual(controller.value_ranges[count][1], value)

    def test_scipy(self):
        """
        ScipyController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = ScipyController(self.cost_func)
        controller.minimizer = 'L-BFGS-B'

        self.check_bounds(controller)

    def test_scipy_ls(self):
        """
        ScipyLSController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = ScipyLSController(self.cost_func)
        controller.minimizer = 'trf'

        self.check_bounds(controller)

    def test_minuit(self):
        """
        MinuitController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = MinuitController(self.cost_func)
        controller.minimizer = 'minuit'

        self.check_bounds(controller)

    def test_dfo(self):
        """
        DFOController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = DFOController(self.cost_func)
        controller.minimizer = 'dfogn'

        self.check_bounds(controller)

    def test_bumps(self):
        """
        BumpsController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = BumpsController(self.cost_func)
        controller.minimizer = 'amoeba'

        self.check_bounds(controller)

    def test_ralfit(self):
        """
        RALFitController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = RALFitController(self.cost_func)
        controller.minimizer = 'gn'

        self.check_bounds(controller)

    def test_levmar(self):
        """
        LevmarController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = LevmarController(self.cost_func)
        controller.minimizer = 'levmar'

        self.check_bounds(controller)

    def test_mantid(self):
        """
        MantidController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        self.check_bounds(controller)

    def test_nlopt(self):
        """
        NLoptController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = NLoptController(self.cost_func)
        controller.minimizer = 'LD_LBFGS'

        self.check_bounds(controller)

    def test_ceres(self):
        """
        CeresController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = CeresController(self.cost_func)
        controller.minimizer = 'Levenberg_Marquardt'

        self.check_bounds(controller)

    def test_lmfit(self):
        """
        LmfitController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = LmfitController(self.cost_func)
        controller.minimizer = 'least_squares'

        self.check_bounds(controller)


@run_for_test_types(TEST_TYPE, 'all')
class ControllerValidateTests(TestCase):
    """
    Tests to ensure controller data is validated correctly.
    """

    def setUp(self):
        """
        Setup for bounded problem
        """
        self.cost_func = make_cost_func("cubic-fba-test-go.txt")

    def test_mantid_controller_does_not_raise(self):
        """
        MantidController: Test that the Mantid controller validation
        does not raise for a valid Jacobian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "2-point"
        self.cost_func.jacobian = self.jac

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        controller.validate()

    def test_mantid_controller_will_raise(self):
        """
        MantidController: Test that the Mantid controller validation
        will raise for an incompatible Jacobian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "cs"
        self.cost_func.jacobian = self.jac

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        with self.assertRaises(exceptions.IncompatibleJacobianError):
            controller.validate()

    def test_scipy_controller_will_raise(self):
        """
        ScipyController: Test that the Scipy controller validation
        will raise for an incompatible Jacobian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "cs"
        self.cost_func.jacobian = self.jac

        controller = ScipyController(self.cost_func)
        controller.minimizer = "L-BFGS-B"

        with self.assertRaises(exceptions.IncompatibleJacobianError):
            controller.validate()

    def test_controller_will_not_raise_for_compatible_jacobian(self):
        """
        ScipyController: Test that the Scipy controller validation
        will not raise for a compatible Jacobian
        """
        self.jac = Default(self.cost_func.problem)
        self.jac.method = "default"
        self.cost_func.jacobian = self.jac

        controller = ScipyController(self.cost_func)
        controller.minimizer = "L-BFGS-B"

        controller.validate()

    def test_mantid_controller_does_not_raise_hessian(self):
        """
        MantidController: Test that the Mantid controller validation
        does not raise for a valid Hessian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "2-point"
        self.cost_func.jacobian = self.jac
        self.hes = ScipyHessian(self.cost_func.problem,
                                self.cost_func.jacobian)
        self.hes.method = "2-point"
        self.cost_func.hessian = self.hes

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        controller.validate()

    def test_mantid_controller_will_raise_hessian(self):
        """
        MantidController: Test that the Mantid controller validation
        will raise for an incompatible Hessian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "2-point"
        self.cost_func.jacobian = self.jac
        self.hes = ScipyHessian(self.cost_func.problem,
                                self.cost_func.jacobian)
        self.hes.method = "cs"
        self.cost_func.hessian = self.hes

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        with self.assertRaises(exceptions.IncompatibleHessianError):
            controller.validate()

    def test_scipy_controller_will_raise_hessian(self):
        """
        ScipyController: Test that the Scipy controller validation
        will raise for an incompatible Hessian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "2-point"
        self.cost_func.jacobian = self.jac
        self.hes = ScipyHessian(self.cost_func.problem,
                                self.cost_func.jacobian)
        self.hes.method = "cs"
        self.cost_func.hessian = self.hes

        controller = ScipyController(self.cost_func)
        controller.minimizer = "L-BFGS-B"

        with self.assertRaises(exceptions.IncompatibleHessianError):
            controller.validate()

    def test_controller_will_not_raise_for_compatible_hessian(self):
        """
        ScipyController: Test that the Scipy controller validation
        will not raise for a compatible Hessian
        """
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = "2-point"
        self.cost_func.jacobian = self.jac
        self.hes = ScipyHessian(self.cost_func.problem,
                                self.cost_func.jacobian)
        self.hes.method = "2-point"
        self.cost_func.hessian = self.hes

        controller = ScipyController(self.cost_func)
        controller.minimizer = "L-BFGS-B"

        controller.validate()


@run_for_test_types(TEST_TYPE, 'all')
class ExternalControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = '2-point'
        self.shared_tests = ControllerSharedTesting()
        self.cost_func.jacobian = self.jac

    def test_levmar(self):
        """
        LevmarController: Tests for output shape
        """
        controller = LevmarController(self.cost_func)
        controller.minimizer = 'levmar'
        self.shared_tests.controller_run_test(controller)

        controller._info = (0, 1, 2, "Stop by small Dp", 4, 5, 6)
        self.shared_tests.check_converged(controller)
        controller._info = (0, 1, 2, "Stopped by small gradient J^T e",
                            4, 5, 6)
        self.shared_tests.check_converged(controller)
        controller._info = (0, 1, 2, "Stopped by small ||e||_2", 4, 5, 6)
        self.shared_tests.check_converged(controller)
        controller._info = (0, 1, 2, "maxit", 4, 5, 6)
        self.shared_tests.check_max_iterations(controller)
        controller._info = (0, 1, 2, "diverged", 4, 5, 6)
        self.shared_tests.check_diverged(controller)

    def test_ceres(self):
        """
        CeresController: Tests for output shape
        """
        controller = CeresController(self.cost_func)

        # test one from each class
        minimizers = ['Levenberg_Marquardt',
                      'BFGS',
                      'Fletcher_Reeves']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 2
            self.shared_tests.check_diverged(controller)

    def test_mantid(self):
        """
        MantidController: Test for output shape
        """
        controller = MantidController(self.cost_func)
        minimizers = ['Levenberg-Marquardt', 'FABADA']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = "success"
            self.shared_tests.check_converged(controller)
            controller._status = "Failed to converge"
            self.shared_tests.check_max_iterations(controller)
            controller._status = "Failed"
            self.shared_tests.check_diverged(controller)

    def test_mantid_default_jacobian(self):
        """
        MantidController: Test for default jacobian
        """
        self.shared_tests = ControllerSharedTesting()
        self.cost_func.jacobian = Default(self.problem)

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'
        self.shared_tests.controller_run_test(controller)

        controller._status = "success"
        self.shared_tests.check_converged(controller)
        controller._status = "Failed to converge"
        self.shared_tests.check_max_iterations(controller)
        controller._status = "Failed"
        self.shared_tests.check_diverged(controller)

    def test_mantid_multifit(self):
        """
        MantidController: Additional bespoke test for multifit
        """

        file_path = os.path.join('multifit_set', 'multifit.txt')
        cost_func = make_cost_func(file_path)

        controller = MantidController(cost_func)
        controller.minimizer = 'Levenberg-Marquardt'

        controller.parameter_set = 0
        controller.prepare()
        controller.fit()
        controller.cleanup()

        self.assertEqual(len(controller.final_params), len(controller.data_x),
                         'Multifit did not return a result for each data file')

        self.assertEqual(len(controller.final_params[0]),
                         len(controller.initial_params),
                         'Incorrect number of final params.')

    def test_mantid_singlefit_chisquared(self):
        """
        Test the override in Mantid conroller is working correctly for
        evaluating chi_squared (SingleFit).
        """
        m_controller = MantidController(self.cost_func)
        b_controller = DummyController(self.cost_func)
        params = np.array([1, 2, 3, 4])
        x = np.array([6, 2, 32, 4])
        y = np.array([1, 21, 3, 4])
        e = np.array([.5, .003, 1, 2])

        expected = b_controller.eval_chisq(params=params, x=x, y=y, e=e)
        actual = m_controller.eval_chisq(params=params, x=x, y=y, e=e)

        self.assertEqual(expected, actual,
                         'Mantid controller found a different chi squared'
                         ' for single fit problem.')

    def test_mantid_multifit_chisquared(self):
        """
        Test the override in Mantid conroller is working correctly for
        evaluating chi_squared (MultiFit).
        """
        m_controller = MantidController(self.cost_func)
        b_controller = DummyController(self.cost_func)
        params = [np.array([1, 2, 3, 4]),
                  np.array([1, 2, 3, 4]),
                  np.array([1, 2, 3, 4])]
        xs = [np.array([6, 2, 32, 4]),
              np.array([6, 2, 32, 4]),
              np.array([6, 2, 32, 4])]
        ys = [np.array([1, 21, 3, 4]),
              np.array([1, 21, 3, 4]),
              np.array([1, 21, 3, 4])]
        es = [np.array([.5, .003, 1, 2]),
              np.array([.5, .003, 1, 2]),
              np.array([.5, .003, 1, 2])]

        expected = [b_controller.eval_chisq(params=p, x=x, y=y, e=e)
                    for x, y, e, p in zip(xs, ys, es, params)]
        actual = m_controller.eval_chisq(params=params, x=xs, y=ys, e=es)

        self.assertListEqual(
            expected, actual,
            'Mantid controller found a different chi squared for multi fit'
            ' problem.')

    def test_gsl(self):
        """
        GSLController: Tests for output shape
        """
        controller = GSLController(self.cost_func)

        # test one from each class
        minimizers = ['lmsder',
                      'nmsimplex',
                      'conjugate_pr']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller.flag = 0
            self.shared_tests.check_converged(controller)
            controller.flag = 1
            self.shared_tests.check_max_iterations(controller)
            controller.flag = 2
            self.shared_tests.check_diverged(controller)

    def test_ralfit(self):
        """
        RALFitController: Tests for output shape
        """
        controller = RALFitController(self.cost_func)

        minimizers = ['gn', 'gn_reg', 'hybrid', 'hybrid_reg']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 2
            self.shared_tests.check_diverged(controller)

    def test_gofit(self):
        """
        GOFitController: Tests for output shape
        """
        controller = GOFitController(self.cost_func)

        minimizers = ['regularisation']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 1
            self.shared_tests.check_max_iterations(controller)


@run_for_test_types(TEST_TYPE, 'matlab')
class MatlabControllerTests(TestCase):
    """
    Tests for each controller class and for the
    Base Matlab Controller
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = '2-point'
        self.cost_func.jacobian = self.jac
        self.shared_tests = ControllerSharedTesting()

    def test_py_to_mat(self):
        """
        Tests the static method py_to_mat in MatlabMixin,
        ensuring that evaluating a function through the matlab
        engine gives the same output as evaulating the function
        from python
        """
        controller = MatlabController(self.cost_func)
        eng = controller.eng
        eng.workspace['test_mat_func'] =\
            controller.py_to_mat('eval_cost')

        params = np.array([1, 2, 3, 4])

        result_py = self.cost_func.eval_cost(params=params)
        result_mat = eng.eval('test_mat_func([1, 2, 3, 4])')
        controller.clear_matlab()
        assert result_py == result_mat

    def test_verify(self):
        """
        MatlabController: Tests for correct error when fitting mantid problem
        """
        # No raise for default (NIST) problem
        controller = MatlabController(self.cost_func)
        controller.validate()
        # Raise for Mantid problem
        cost_func = make_cost_func('cubic-fba-test-go.txt')
        jac = Scipy(cost_func.problem)
        jac.method = '2-point'
        cost_func.jacobian = jac
        controller = MatlabController(cost_func)
        with self.assertRaises(exceptions.IncompatibleProblemError):
            controller.validate()
        controller.clear_matlab()

    def test_matlab(self):
        """
        MatlabController: Tests for output shape
        """
        controller = MatlabController(self.cost_func)

        minimizers = ['Nelder-Mead Simplex']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 1
            self.shared_tests.check_converged(controller)
            controller._status = 0
            self.shared_tests.check_max_iterations(controller)
            controller._status = -1
            self.shared_tests.check_diverged(controller)
            controller.clear_matlab()

    def test_matlab_opt(self):
        """
        MatlabOptController: Tests for output shape
        """
        controller = MatlabOptController(self.cost_func)

        minimizers = ['levenberg-marquardt', 'trust-region-reflective']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 1
            self.shared_tests.check_converged(controller)
            controller._status = 0
            self.shared_tests.check_max_iterations(controller)
            controller._status = -1
            self.shared_tests.check_diverged(controller)
            controller.clear_matlab()

    def test_matlab_stats(self):
        """
        MatlabStatsController: Tests for output shape
        """
        controller = MatlabStatsController(self.cost_func)

        minimizers = ['Levenberg-Marquardt']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 1
            self.shared_tests.check_diverged(controller)
            controller.clear_matlab()

    def test_matlab_curve(self):
        """
        MatlabCurveController: Tests for output shape
        """
        controller = MatlabCurveController(self.cost_func)

        minimizers = ['Levenberg-Marquardt', 'Trust-Region']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 1
            self.shared_tests.check_converged(controller)
            controller._status = 0
            self.shared_tests.check_max_iterations(controller)
            controller._status = -1
            self.shared_tests.check_diverged(controller)
            controller.clear_matlab()

    def test_horace(self):
        """
        Horace: Tests for output shape
        """
        controller = HoraceController(self.cost_func)

        minimizers = ['lm-lsqr']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._fit_params['converged'] = 1
            self.shared_tests.check_converged(controller)
            controller._fit_params['converged'] = 0
            self.shared_tests.check_diverged(controller)
            controller.clear_matlab()


@run_for_test_types(TEST_TYPE, 'all')
class GlobalOptimizationControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func('cubic-fba-test-go.txt')
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func.problem)
        self.jac.method = '2-point'
        self.cost_func.jacobian = self.jac
        self.shared_tests = ControllerSharedTesting()

    def test_scipy_go(self):
        """
        ScipyGOController: Test for output shape
        """
        controller = ScipyGOController(self.cost_func)
        controller.minimizer = 'dual_annealing'

        self.shared_tests.controller_run_test(controller)

        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 1
        self.shared_tests.check_max_iterations(controller)
        controller._status = 2
        self.shared_tests.check_diverged(controller)

    def test_gradient_free(self):
        """
        GradientFreeController: Tests for output shape
        """
        controller = GradientFreeController(self.cost_func)
        controller.minimizer = 'HillClimbingOptimizer'
        self.shared_tests.controller_run_test(controller)

        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 2
        self.shared_tests.check_diverged(controller)


@run_for_test_types(TEST_TYPE, 'default', 'all')
class FactoryTests(TestCase):
    """
    Tests for the ControllerFactory
    """

    def test_default_imports(self):
        """
        Test that the factory returns the correct default class for inputs
        """
        valid = ['scipy_ls', 'bumps']
        valid_names = ['scipyls', 'bumps']
        invalid = ['foo', 'bar', 'hello', 'r2d2']
        self.check_valid(valid, valid_names)
        self.check_invalid(invalid)

    @run_for_test_types(TEST_TYPE, 'all')
    def test_external_imports(self):
        """
        Test that the factory returns the correct external class for inputs
        """
        valid = ['mantid', 'ralfit']
        valid_names = ['mantid', 'ralfit']
        self.check_valid(valid, valid_names)

    def check_valid(self, valid, valid_names):
        '''
        Check that correct controller generated for valid
        software names
        '''
        for software, v in zip(valid, valid_names):
            controller = ControllerFactory.create_controller(software)
            self.assertTrue(controller.__name__.lower().startswith(v))

    def check_invalid(self, invalid):
        '''
        Check that correct exception is raised when invalid
        software name is used.
        '''
        for software in invalid:
            self.assertRaises(exceptions.NoControllerError,
                              ControllerFactory.create_controller,
                              software)
