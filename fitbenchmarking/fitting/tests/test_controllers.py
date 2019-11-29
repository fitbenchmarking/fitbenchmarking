import inspect
import os
from unittest import TestCase

import benchmark_problems
from fitbenchmarking.fitting.controllers.base_controller import \
    Controller
from fitbenchmarking.fitting.controllers.controller_factory import \
    ControllerFactory
from fitbenchmarking.fitting.controllers.dfogn_controller import \
    DFOGNController
from fitbenchmarking.fitting.controllers.mantid_controller import \
    MantidController
from fitbenchmarking.fitting.controllers.minuit_controller import \
    MinuitController
from fitbenchmarking.fitting.controllers.ralfit_controller import \
    RALFitController
from fitbenchmarking.fitting.controllers.sasview_controller import \
    SasviewController
from fitbenchmarking.fitting.controllers.scipy_controller import \
    ScipyController

from fitbenchmarking.parsing.parser_factory import parse_problem_file


def make_fitting_problem():
    """
    Helper function that returns a simple fitting problem
    """

    bench_prob_dir = os.path.dirname(inspect.getfile(benchmark_problems))
    fname = os.path.join(bench_prob_dir, 'simple_tests',
                         'cubic.dat')

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
        controller.minimizer = 'SteepestDescent'
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
        :type contrller: Object derived from BaseSoftwareController
        """
        controller.parameter_set = 0
        controller.prepare()
        controller.fit()
        controller.cleanup()

        assert controller.success
        assert len(controller.results) == len(controller.data_y)
        assert len(controller.final_params) == len(controller.initial_params)


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
