# Tests for the controllers available from a default fitbenchmarking install
import inspect
import numpy as np
import os
from unittest import TestCase

from fitbenchmarking import mock_problems
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.controllers.dfo_controller import DFOController
from fitbenchmarking.controllers.minuit_controller import MinuitController
from fitbenchmarking.controllers.sasview_controller import SasviewController
from fitbenchmarking.controllers.scipy_controller import ScipyController
from fitbenchmarking.controllers.scipy_ls_controller import ScipyLSController

from fitbenchmarking.parsing.parser_factory import parse_problem_file
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


def make_fitting_problem(file_name='cubic.dat'):
    """
    Helper function that returns a simple fitting problem
    """
    options = Options()

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
    fname = os.path.join(bench_prob_dir, file_name)

    fitting_problem = parse_problem_file(fname, options)
    fitting_problem.correct_data()
    return fitting_problem


class DummyController(Controller):
    """
    Minimal instantiatable subclass of Controller class for testing
    """

    def setup(self):
        self.setup_result = 53

    def fit(self):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def error_flags(self):
        raise NotImplementedError


class BaseControllerTests(TestCase):
    """
    Tests for base software controller class methods.
    """

    def setUp(self):
        self.problem = make_fitting_problem()

    def test_data(self):
        """
        BaseSoftwareController: Test data is read into controller correctly
        """

        controller = DummyController(self.problem)

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
        controller = DummyController(self.problem)
        controller.minimizer = 'test'
        controller.parameter_set = 0
        controller.prepare()
        assert controller.setup_result == 53

    def test_eval_chisq_no_errors(self):
        """
        BaseSoftwareController: Test eval_chisq function
        """
        controller = DummyController(self.problem)

        params = np.array([1, 2, 3, 4])
        x = np.array([6, 2, 32, 4])
        y = np.array([1, 21, 3, 4])
        e = None

        result = self.problem.eval_r_norm(params=params, x=x, y=y, e=e)

        assert controller.eval_chisq(params=params, x=x, y=y, e=e) == result

    def test_eval_chisq_with_errors(self):
        """
        BaseSoftwareController: Test eval_chisq function
        """
        controller = DummyController(self.problem)

        params = np.array([1, 2, 3, 4])
        x = np.array([6, 2, 32, 4])
        y = np.array([1, 21, 3, 4])
        e = np.array([.5, .003, 1, 2])

        result = self.problem.eval_r_norm(params=params, x=x, y=y, e=e)

        assert controller.eval_chisq(params=params, x=x, y=y, e=e) == result

    def test_check_flag_attr_true(self):
        """
        BaseSoftwareController: Test check_attributes function for flag
                                attribute
        """
        controller = DummyController(self.problem)
        controller.flag = 1
        controller.check_attributes()

    def test_check_flag_attr_false(self):
        """
        BaseSoftwareController: Test check_attributes function for flag
                                attribute
        """
        controller = DummyController(self.problem)
        with self.assertRaises(exceptions.ControllerAttributeError):
            controller.check_attributes()

        controller.flag = 10
        with self.assertRaises(exceptions.ControllerAttributeError):
            controller.check_attributes()


class ControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.problem = make_fitting_problem()

    def test_sasview(self):
        """
        SasviewController: Test for output shape
        """
        controller = SasviewController(self.problem)
        controller.minimizer = 'amoeba'
        self.shared_testing(controller)

        controller._status = 0
        self.check_converged(controller)
        controller._status = 2
        self.check_max_iterations(controller)
        controller._status = 1
        self.check_diverged(controller)

    def test_scipy_ls(self):
        """
        ScipyController: Test for output shape
        """
        controller = ScipyLSController(self.problem)
        controller.minimizer = 'lm'
        self.shared_testing(controller)

        controller._status = 1
        self.check_converged(controller)
        controller._status = 0
        self.check_max_iterations(controller)
        controller._status = -1
        self.check_diverged(controller)

    def test_scipy(self):
        """
        ScipyController: Test for output shape
        """
        controller = ScipyController(self.problem)
        controller.minimizer = 'CG'
        self.shared_testing(controller)

        controller._status = 1
        self.check_converged(controller)
        controller._status = 0
        self.check_max_iterations(controller)
        controller._status = -1
        self.check_diverged(controller)

    def test_dfo(self):
        """
        DFOController: Tests for output shape
        """
        controller = DFOController(self.problem)
        # test one from each class
        minimizers = ['dfogn',
                      'dfols']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_testing(controller)

            controller._status = 0
            self.check_converged(controller)
            controller._status = 2
            self.check_max_iterations(controller)
            controller._status = 5
            self.check_diverged(controller)

    def test_minuit(self):
        """
        MinuitController: Tests for output shape
        """
        controller = MinuitController(self.problem)
        controller.minimizer = 'minuit'
        self.shared_testing(controller)
        controller._status = 0
        self.check_converged(controller)
        controller._status = 2
        self.check_diverged(controller)

    def shared_testing(self, controller):
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


class FactoryTests(TestCase):
    """
    Tests for the ControllerFactory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """

        valid = ['scipy_ls', 'mantid', 'sasview', 'ralfit']
        valid_names = ['scipyls', 'mantid', 'sasview', 'ralfit']
        invalid = ['foo', 'bar', 'hello', 'r2d2']

        for software, v in zip(valid, valid_names):
            controller = ControllerFactory.create_controller(software)
            print(controller.__name__.lower())
            self.assertTrue(controller.__name__.lower().startswith(v))

        for software in invalid:
            self.assertRaises(exceptions.NoControllerError,
                              ControllerFactory.create_controller,
                              software)
