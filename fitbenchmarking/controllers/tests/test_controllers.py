import inspect
import numpy as np
import os
from unittest import TestCase

from fitbenchmarking import mock_problems
from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.controller_factory import ControllerFactory
from fitbenchmarking.controllers.dfogn_controller import DFOGNController
from fitbenchmarking.controllers.gsl_controller import GSLController
from fitbenchmarking.controllers.mantid_controller import MantidController
from fitbenchmarking.controllers.minuit_controller import MinuitController
from fitbenchmarking.controllers.ralfit_controller import RALFitController
from fitbenchmarking.controllers.sasview_controller import SasviewController
from fitbenchmarking.controllers.scipy_controller import ScipyController

from fitbenchmarking.parsing.parser_factory import parse_problem_file


def make_fitting_problem():
    """
    Helper function that returns a simple fitting problem
    """

    bench_prob_dir = os.path.dirname(inspect.getfile(mock_problems))
    fname = os.path.join(bench_prob_dir, 'cubic.dat')

    fitting_problem = parse_problem_file(fname)
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

        controller = DummyController(self.problem, True)

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

    def test_no_use_errors(self):
        """
        BaseSoftwareController: Test errors are not set when not requested
        """
        controller = DummyController(self.problem, False)
        assert controller.data_e is None

    def test_prepare(self):
        """
        BaseSoftwareController: Test prepare function
        """
        controller = DummyController(self.problem, True)
        controller.minimizer = 'test'
        controller.parameter_set = 0
        controller.prepare()
        assert controller.setup_result == 53

    def test_eval_chisq_no_errors(self):
        """
        BaseSoftwareController: Test eval_chisq function
        """
        controller = DummyController(self.problem, True)

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
        controller = DummyController(self.problem, True)

        params = np.array([1, 2, 3, 4])
        x = np.array([6, 2, 32, 4])
        y = np.array([1, 21, 3, 4])
        e = np.array([.5, .003, 1, 2])

        result = self.problem.eval_r_norm(params=params, x=x, y=y, e=e)

        assert controller.eval_chisq(params=params, x=x, y=y, e=e) == result


class ControllerTests(TestCase):
    """
    Tests for each controller class
    """

    def setUp(self):
        self.problem = make_fitting_problem()

    def test_mantid(self):
        """
        MantidController: Test for output shape
        """
        controller = MantidController(self.problem, True)
        controller.minimizer = 'Levenberg-Marquardt'
        self.shared_testing(controller)

    def test_sasview(self):
        """
        SasviewController: Test for output shape
        """
        controller = SasviewController(self.problem, True)
        controller.minimizer = 'amoeba'
        self.shared_testing(controller)

    def test_scipy(self):
        """
        ScipyController: Test for output shape
        """
        controller = ScipyController(self.problem, True)
        controller.minimizer = 'lm'
        self.shared_testing(controller)

    def test_dfogn(self):
        """
        DFOGNController: Tests for output shape
        """
        controller = DFOGNController(self.problem, True)
        controller.minimizer = 'dfogn'
        self.shared_testing(controller)

    def test_gsl(self):
        """
        GSLController: Tests for output shape
        """
        controller = GSLController(self.problem, True)
        # test one from each class
        minimizers = ['lmsder',
                      'nmsimplex',
                      'conjugate_pr']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_testing(controller)

    def test_ralfit(self):
        """
        RALFitController: Tests for output shape
        """
        controller = RALFitController(self.problem, True)
        minimizers = ['gn', 'gn_reg', 'hybrid', 'hybrid_reg']
        for minimizer in minimizers:
            controller.minimizer = minimizer
            self.shared_testing(controller)

    def test_minuit(self):
        """
        MinuitController: Tests for output shape
        """
        controller = MinuitController(self.problem, True)
        controller.minimizer = 'minuit'
        self.shared_testing(controller)

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
        controller.error_flags()

        assert controller.success
        assert len(controller.results) == len(controller.data_y)
        assert len(controller.final_params) == len(controller.initial_params)
        assert controller.flag == 0


class ErrorFlagsTest(TestCase):

    def setUp(self):
        self.problem = make_fitting_problem()

    def test_mantid(self):
        """
        MantidController: Test for output shape
        """
        controller = MantidController(self.problem, True)
        controller._status = "success"
        self.check_conveged(controller)
        controller._status = "Failed to converge"
        self.check_max_iterations(controller)
        controller._status = "Failed"
        self.check_diverged(controller)

    def test_sasview(self):
        """
        SasviewController: Test for output shape
        """
        controller = SasviewController(self.problem, True)
        controller._status = 0
        self.check_conveged(controller)
        controller._status = 2
        self.check_max_iterations(controller)
        controller._status = 1
        self.check_diverged(controller)

    def test_scipy(self):
        """
        ScipyController: Test for output shape
        """
        controller = ScipyController(self.problem, True)
        controller._status = 1
        self.check_conveged(controller)
        controller._status = 0
        self.check_max_iterations(controller)
        controller._status = -1
        self.check_diverged(controller)

    def test_dfogn(self):

        # DFOGNController: Tests for output shape

        controller = DFOGNController(self.problem, True)
        controller._status = 0
        self.check_conveged(controller)
        controller._status = 2
        self.check_max_iterations(controller)
        controller._status = 5
        self.check_diverged(controller)

    def test_gsl(self):
        """
        GSLController: Tests for output shape
        """
        controller = GSLController(self.problem, True)
        controller._status = 0
        self.check_conveged(controller)
        controller._status = 1
        self.check_max_iterations(controller)
        controller._status = 2
        self.check_diverged(controller)

    def test_ralfit(self):
        """
        RALFitController: Tests for output shape
        """
        controller = RALFitController(self.problem, True)
        controller._status = 0
        self.check_conveged(controller)
        controller._status = 2
        self.check_diverged(controller)

    def test_minuit(self):
        """
        MinuitController: Tests for output shape
        """
        controller = MinuitController(self.problem, True)
        controller.minimizer = 'minuit'
        controller.parameter_set = 0

        controller.prepare()
        controller.fit()
        controller._status = 0
        self.check_conveged(controller)
        controller._status = 2
        self.check_diverged(controller)

    def check_conveged(self, controller):
        """
        Utility function to run controller and check output is in generic form

        :param controller: Controller to test, with setup already completed
        :type contrller: Object derived from BaseSoftwareController
        """
        controller.error_flags()
        assert controller.flag == 0

    def check_max_iterations(self, controller):
        """
        Utility function to run controller and check output is in generic form

        :param controller: Controller to test, with setup already completed
        :type contrller: Object derived from BaseSoftwareController
        """
        controller.error_flags()
        assert controller.flag == 1

    def check_diverged(self, controller):
        """
        Utility function to run controller and check output is in generic form

        :param controller: Controller to test, with setup already completed
        :type contrller: Object derived from BaseSoftwareController
        """
        controller.error_flags()
        assert controller.flag == 2


class FactoryTests(TestCase):
    """
    Tests for the ControllerFactory
    """

    def test_imports(self):
        """
        Test that the factory returns the correct class for inputs
        """

        valid = ['scipy', 'mantid', 'sasview', 'ralfit']
        invalid = ['foo', 'bar', 'hello', 'r2d2']

        for software in valid:
            controller = ControllerFactory.create_controller(software)
            self.assertTrue(controller.__name__.lower().startswith(software))

        for software in invalid:
            self.assertRaises(ValueError,
                              ControllerFactory.create_controller,
                              software)
