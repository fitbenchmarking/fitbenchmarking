"""
Tests for the controllers available from a default fitbenchmarking install
"""
import inspect
import os
from unittest import TestCase
import numpy as np
from pytest import test_type as TEST_TYPE  # pylint: disable=no-name-in-module

from fitbenchmarking.controllers.base_controller import Controller

from fitbenchmarking.cost_func.weighted_nlls_cost_func import \
    WeightedNLLSCostFunc
from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options
from fitbenchmarking.jacobian.scipy_jacobian import Scipy
from conftest import run_for_test_types

from fitbenchmarking import mock_problems

if TEST_TYPE in ['default', 'all']:
    from fitbenchmarking.controllers.bumps_controller import BumpsController
    from fitbenchmarking.controllers.controller_factory import\
        ControllerFactory
    from fitbenchmarking.controllers.dfo_controller import DFOController
    from fitbenchmarking.controllers.minuit_controller import\
        MinuitController
    from fitbenchmarking.controllers.scipy_controller import ScipyController
    from fitbenchmarking.controllers.scipy_ls_controller import\
        ScipyLSController
    from fitbenchmarking.controllers.scipy_go_controller import\
        ScipyGOController

if TEST_TYPE == 'all':
    from fitbenchmarking.controllers.gsl_controller import GSLController
    from fitbenchmarking.controllers.levmar_controller import LevmarController
    from fitbenchmarking.controllers.mantid_controller import MantidController
    from fitbenchmarking.controllers.ralfit_controller import RALFitController

if TEST_TYPE == 'matlab':
    from fitbenchmarking.controllers.matlab_controller import MatlabController


# pylint: disable=attribute-defined-outside-init, protected-access


def make_cost_func(file_name='cubic.dat'):
    """
    Helper function that returns a simple fitting problem
    """

    options = Options()

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
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
    '''
    Tests used by all controllers
    '''

    def controller_run_test(self, controller):
        """
        Utility function to run controller and check output is in generic form

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.parameter_set = 0
        controller.prepare()
        controller.fit()
        controller.cleanup()

        assert len(controller.final_params) == len(controller.initial_params)

    def check_jac_info(self, controller, expected_has_jac, expected_jac_list):
        """
        Utility function to check controller.jacobian_information() produces
        a success flag

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        :param expected_has_jac: expected has_jacobian value
        :type expected_has_jac: bool
        :param expected_jac_list: expected jacobian_list value
        :type expected_jac_list: list
        """
        has_jacobian, jacobian_list = controller.jacobian_information()
        assert has_jacobian == expected_has_jac
        assert jacobian_list == expected_jac_list

    def check_converged(self, controller):
        """
        Utility function to check controller.cleanup() produces a success flag

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.cleanup()
        assert controller.flag == 0

    def check_max_iterations(self, controller):
        """
        Utility function to check controller.cleanup() produces a maximum
        iteration flag

        :param controller: Controller to test, with setup already completed
        :type controller: Object derived from BaseSoftwareController
        """
        controller.cleanup()
        assert controller.flag == 1

    def check_diverged(self, controller):
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


@run_for_test_types(TEST_TYPE, 'default', 'all')
class DefaultControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func)
        self.jac.method = '2-point'
        self.shared_tests = ControllerSharedTesting()

    def test_bumps(self):
        """
        BumpsController: Test for output shape
        """
        controller = BumpsController(self.cost_func)
        controller.minimizer = 'amoeba'
        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         False,
                                         [])

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
        self.shared_tests.check_jac_info(controller,
                                         False,
                                         [])
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
        self.shared_tests.check_jac_info(controller,
                                         False,
                                         [])

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
        controller.jacobian = self.jac
        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         ["Nelder-Mead", "Powell"])
        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 2
        self.shared_tests.check_max_iterations(controller)
        controller._status = 1
        self.shared_tests.check_diverged(controller)

    def test_scipy_ls(self):
        """
        ScipyLSController: Test for output shape
        """
        controller = ScipyLSController(self.cost_func)
        controller.minimizer = 'lm'
        controller.jacobian = self.jac

        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         [None])

        controller._status = 1
        self.shared_tests.check_converged(controller)
        controller._status = 0
        self.shared_tests.check_max_iterations(controller)
        controller._status = -1
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
        self.jac = Scipy(self.cost_func)
        self.jac.method = '2-point'

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
            assert controller.value_ranges[count][0] <= value \
                <= controller.value_ranges[count][1]

    def test_scipy(self):
        """
        ScipyController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = ScipyController(self.cost_func)
        controller.minimizer = 'L-BFGS-B'
        controller.jacobian = self.jac

        self.check_bounds(controller)

    def test_scipy_ls(self):
        """
        ScipyLSController: Test that parameter bounds are
        respected for bounded problems
        """
        controller = ScipyLSController(self.cost_func)
        controller.minimizer = 'trf'
        controller.jacobian = self.jac

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
        controller.jacobian = self.jac

        self.check_bounds(controller)

    def test_levmar(self):
        """
        LevmarController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = LevmarController(self.cost_func)
        controller.minimizer = 'levmar'
        controller.jacobian = self.jac

        self.check_bounds(controller)

    def test_mantid(self):
        """
        MantidController: Test that parameter bounds are
        respected for bounded problems
        """

        controller = MantidController(self.cost_func)
        controller.minimizer = 'Levenberg-Marquardt'
        controller.jacobian = self.jac

        self.check_bounds(controller)


@run_for_test_types(TEST_TYPE, 'all')
class ExternalControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func)
        self.jac.method = '2-point'
        self.shared_tests = ControllerSharedTesting()

    def test_levmar(self):
        """
        LevmarController: Tests for output shape
        """
        controller = LevmarController(self.cost_func)
        controller.minimizer = 'levmar'
        controller.jacobian = self.jac
        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         [])

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

    def test_mantid(self):
        """
        MantidController: Test for output shape
        """
        controller = MantidController(self.cost_func)
        controller.jacobian = self.jac
        controller.minimizer = 'Levenberg-Marquardt'
        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         ["Simplex"])
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
        controller.jacobian = self.jac
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         ["nmsimplex", "nmsimplex2"])
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
        controller.jacobian = self.jac
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         [])

        minimizers = ['gn', 'gn_reg', 'hybrid', 'hybrid_reg']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_tests.controller_run_test(controller)

            controller._status = 0
            self.shared_tests.check_converged(controller)
            controller._status = 2
            self.shared_tests.check_diverged(controller)


@run_for_test_types(TEST_TYPE, 'matlab')
class MatlabControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func()
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func)
        self.jac.method = '2-point'
        self.shared_tests = ControllerSharedTesting()

    def test_matlab(self):
        """
        MatlabController: Tests for output shape
        """
        controller = MatlabController(self.cost_func)
        controller.jacobian = self.jac
        self.shared_tests.check_jac_info(controller,
                                         False,
                                         [])

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


@run_for_test_types(TEST_TYPE, 'all')
class GlobalOptimizationControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.cost_func = make_cost_func('cubic-fba-test-go.txt')
        self.problem = self.cost_func.problem
        self.jac = Scipy(self.cost_func)
        self.jac.method = '2-point'
        self.shared_tests = ControllerSharedTesting()

    def test_scipy_go(self):
        """
        ScipyGOController: Test for output shape
        """
        controller = ScipyGOController(self.cost_func)
        controller.minimizer = 'dual_annealing'
        controller.jacobian = self.jac

        self.shared_tests.controller_run_test(controller)
        self.shared_tests.check_jac_info(controller,
                                         True,
                                         ['differential_evolution'])

        controller._status = 0
        self.shared_tests.check_converged(controller)
        controller._status = 1
        self.shared_tests.check_max_iterations(controller)
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
