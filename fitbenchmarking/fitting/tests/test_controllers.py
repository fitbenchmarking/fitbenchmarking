import os
import unittest

from fitbenchmarking.fitting.software_controllers.base_software_controller import \
    BaseSoftwareController
from fitbenchmarking.fitting.software_controllers.mantid_controller import \
    MantidController
from fitbenchmarking.fitting.software_controllers.sasview_controller import \
    SasviewController
from fitbenchmarking.fitting.software_controllers.scipy_controller import \
    ScipyController
from fitbenchmarking.parsing.parse_nist_data import FittingProblem


def misra1a_file():
    """
    Helper function that returns the path to
    /fitbenchmarking/benchmark_problems
    """

    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(os.path.normpath(current_dir))
    main_dir = os.path.dirname(os.path.normpath(parent_dir))
    root_dir = os.path.dirname(os.path.normpath(main_dir))
    bench_prob_dir = os.path.join(root_dir, 'benchmark_problems')
    fname = os.path.join(bench_prob_dir, 'NIST', 'low_difficulty',
                         'Misra1a.dat')

    return fname


class DummyController(BaseSoftwareController):
    def setup(self):
        self.setup_result = 53

    def fit(self):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError


class BaseSoftwareControllerTests(unittest.TestCase):
    def setUp(self):
        self.problem = FittingProblem(misra1a_file())

    def test_data(self):
        controller = DummyController(self.problem, True)
        assert(min(controller.data_x) >= self.problem.start_x)
        assert(max(controller.data_x) <= self.problem.end_x)
        assert(len(controller.data_e) == len(controller.data_x))
        assert(len(controller.data_e) == len(controller.data_y))
        x_is_subset = all(x in self.problem._data_x
                          for x in controller.data_x)
        y_is_subset = all(y in self.problem._data_y
                          for y in controller.data_y)

        e_is_default = self.problem.data_e is None
        e_is_subset = False
        if not e_is_default:
            e_is_subset = all(e in self.problem._data_e
                              for e in controller.data_e)
        assert(x_is_subset
               and y_is_subset
               and (e_is_subset or e_is_default))

    def test_no_use_errors(self):
        controller = DummyController(self.problem, False)
        assert(controller.data_e is None)

    def test_prepare(self):
        controller = DummyController(self.problem, True)
        controller.prepare(minimizer='test')
        assert(controller.minimizer == 'test')
        controller.prepare(function_id=0)
        assert(controller.function_id == 0)
        assert(controller.setup_result == 53)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.problem = FittingProblem(misra1a_file())

    def test_mantid(self):
        controller = MantidController(self.problem, True)
        controller.prepare(function_id=0)
        controller.prepare(minimizer='SteepestDescent')
        self.shared_testing(controller)

    def test_sasview(self):
        controller = SasviewController(self.problem, True)
        controller.prepare(function_id=0)
        controller.prepare(minimizer='amoeba')
        self.shared_testing(controller)

    def test_scipy(self):
        controller = ScipyController(self.problem, True)
        controller.prepare(function_id=0)
        controller.prepare(minimizer='lm')
        self.shared_testing(controller)

    def shared_testing(self, controller):
        controller.fit()
        controller.cleanup()

        assert(controller.success)
        assert(len(controller.results) == len(controller.data_y))
        assert(len(controller.final_params) == len(controller.initial_params))
    
