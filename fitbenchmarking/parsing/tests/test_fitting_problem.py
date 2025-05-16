"""
Test file to test the fitting_problem file.
"""

from unittest import TestCase
from unittest.mock import patch

import numpy as np
from parameterized import parameterized

from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


class TestFittingProblem(TestCase):
    """
    Class to test the FittingProblem class
    """

    def setUp(self):
        """
        Setting up FittingProblem tests
        """
        self.options = Options()

    def test_fitting_problem_str(self):
        """
        Test that the fitting problem can be printed as a readable string.
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.name = "Fake"
        fitting_problem.format = "nist"
        fitting_problem.equation = "b1*x"
        fitting_problem.start_x = 0.5
        fitting_problem.end_x = 2.5
        fitting_problem.multifit = False

        self.assertEqual(
            str(fitting_problem),
            "+==================+\n"
            "| FittingProblem   |\n"
            "+==================+\n"
            "| Name     | Fake  |\n"
            "+------------------+\n"
            "| Format   | nist  |\n"
            "+------------------+\n"
            "| Equation | b1*x  |\n"
            "+------------------+\n"
            "| Params   | None  |\n"
            "+------------------+\n"
            "| Start X  | 0.5   |\n"
            "+------------------+\n"
            "| End X    | 2.5   |\n"
            "+------------------+\n"
            "| MultiFit | False |\n"
            "+------------------+",
        )

    def test_verify_problem(self):
        """
        Test that verify only passes if all required values are set.
        """
        fitting_problem = FittingProblem(self.options)
        with self.assertRaises(exceptions.FittingProblemError):
            fitting_problem.verify()
            self.fail("verify() passes when no values are set.")

        fitting_problem.starting_values = [{"p1": 1, "p2": 2}]
        with self.assertRaises(exceptions.FittingProblemError):
            fitting_problem.verify()
            self.fail("verify() passes starting values are set.")

        fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        with self.assertRaises(exceptions.FittingProblemError):
            fitting_problem.verify()
            self.fail("verify() passes when data_x is set.")

        fitting_problem.data_y = np.array([1, 2, 3, 4, 5])
        with self.assertRaises(exceptions.FittingProblemError):
            fitting_problem.verify()
            self.fail("verify() passes when data_y is set.")

        fitting_problem.function = lambda x, p1, p2: p1 + p2
        try:
            fitting_problem.verify()
        except exceptions.FittingProblemError:
            self.fail("verify() fails when all required values set.")

        fitting_problem.data_x = [1, 2, 3]
        with self.assertRaises(exceptions.FittingProblemError):
            fitting_problem.verify()
            self.fail("verify() passes for x values not numpy.")

    def test_eval_model_raise_error(self):
        """
        Test that eval_model raises an error if there is no function
        """
        fitting_problem = FittingProblem(self.options)
        self.assertRaises(
            exceptions.FittingProblemError,
            fitting_problem.eval_model,
            x=2,
            params=[1, 2, 3],
        )

    def test_eval_model_correct_evaluation(self):
        """
        Test that eval_model is running the correct function
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.function = lambda x, p1: x + p1
        x_val = np.array([1, 8, 11])
        eval_result = fitting_problem.eval_model(x=x_val, params=[5])
        self.assertTrue(all(eval_result == np.array([6, 13, 16])))

        fitting_problem.data_x = np.array([20, 21, 22])
        eval_result = fitting_problem.eval_model(params=[5])
        self.assertTrue(all(eval_result == np.array([25, 26, 27])))

    def test_get_function_params(self):
        """
        Tests that the function params is formatted correctly
        """
        fitting_problem = FittingProblem(self.options)
        expected_function_def = "a=1, b=2.0, c=3.3, d=4.99999"
        fitting_problem.starting_values = [{"a": 0, "b": 0, "c": 0, "d": 0}]
        params = [1, 2.0, 3.3, 4.99999]
        function_def = fitting_problem.get_function_params(params=params)
        self.assertEqual(function_def, expected_function_def)

    def test_set_value_ranges(self):
        """
        Tests that value_ranges are formatted correctly
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.starting_values = [
            {"param1": 0, "param2": 0, "param3": 0}
        ]
        value_ranges_prob_def = {"param1": (0, 5), "param2": (5, 10)}
        expected_value_ranges = [(0, 5), (5, 10), (-np.inf, np.inf)]
        fitting_problem.set_value_ranges(value_ranges_prob_def)
        self.assertEqual(fitting_problem.value_ranges, expected_value_ranges)

    def test_set_value_ranges_incorrect_names(self):
        """
        Tests that an exception is raised if parameter names
        in `parameter_ranges` are incorrect
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.starting_values = [
            {"param1": 0, "param2": 0, "param3": 0}
        ]
        value_ranges_prob_def = {"incorrect_name": (0, 5), "param2": (5, 10)}
        self.assertRaises(
            exceptions.IncorrectBoundsError,
            fitting_problem.set_value_ranges,
            value_ranges_prob_def,
        )

    def test_correct_data_single_fit(self):
        """
        Tests that correct data gives the expected result
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.data_x = np.array(
            [-0.5, 0.0, 1.0, 0.5, 1.5, 2.0, 2.5, 3.0, 4.0]
        )
        fitting_problem.data_y = np.array(
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        )
        fitting_problem.data_e = np.array(
            [1.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 9.0]
        )
        fitting_problem.start_x = 0.5
        fitting_problem.end_x = 2.5

        expected_x_data = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
        expected_y_data = np.array([3.0, 2.0, 4.0, 5.0, 6.0])
        expected_e_data = np.array([40.0, 30.0, 50.0, 60.0, 70.0])

        fitting_problem.correct_data()

        sort = fitting_problem.sorted_index
        self.assertTrue(
            (fitting_problem.data_x[sort] == expected_x_data).all()
        )
        self.assertTrue(
            (fitting_problem.data_y[sort] == expected_y_data).all()
        )
        self.assertTrue(
            (fitting_problem.data_e[sort] == expected_e_data).all()
        )

        self.options.cost_func_type = ["nlls"]
        fitting_problem.correct_data()
        self.assertTrue(
            (fitting_problem.data_x[sort] == expected_x_data).all()
        )
        self.assertTrue(
            (fitting_problem.data_y[sort] == expected_y_data).all()
        )
        self.assertIs(fitting_problem.data_e, None)

    def test_correct_data_multi_fit(self):
        """
        Tests correct data on a multifit problem.
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.multifit = True
        fitting_problem.data_x = [
            np.array([-0.5, 0.0, 1.0, 0.5, 1.5, 2.0, 2.5, 3.0, 4.0]),
            np.array([-0.5, 0.0, 1.0, 0.5, 1.4, 2.0, 2.5, 3.0, 4.0]),
            np.array([-0.5, 0.0, 1.0, 0.5, 1.7, 2.0, 2.5, 3.0, 4.0]),
        ]
        fitting_problem.data_y = [
            np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]),
            np.array([0.0, 1.0, 2.0, 3.0, 24.0, 5.0, 6.0, 7.0, 8.0]),
            np.array([0.0, 1.0, 2.8, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]),
        ]
        fitting_problem.data_e = [
            np.array([1.0, 20.0, 30.0, 40.0, 50.0, 60.0, 1.0, 6.0, 9.0]),
            np.array([1.0, 20.0, 30.0, 40.0, 50.0, 60.0, 1.0, 6.0, 9.0]),
            np.array([1.0, 20.0, 30.0, 40.0, 50.0, 60.0, 1.0, 6.0, 9.0]),
        ]
        fitting_problem.start_x = [0.5, 1.1, 0.0]
        fitting_problem.end_x = [2.5, 2.6, 1.0]

        expected_x_data = [
            np.array([0.5, 1.0, 1.5, 2.0, 2.5]),
            np.array([1.4, 2.0, 2.5]),
            np.array([0.0, 0.5, 1.0]),
        ]
        expected_y_data = [
            np.array([3.0, 2.0, 4.0, 5.0, 6.0]),
            np.array([24.0, 5.0, 6.0]),
            np.array([1.0, 3.0, 2.8]),
        ]
        expected_e_data = [
            np.array([40.0, 30.0, 50.0, 60.0, 1.0]),
            np.array([50.0, 60.0, 1.0]),
            np.array([20.0, 40.0, 30.0]),
        ]

        fitting_problem.correct_data()

        for ix, sort in enumerate(fitting_problem.sorted_index):
            self.assertTrue(
                (fitting_problem.data_x[ix][sort] == expected_x_data[ix]).all()
            )
            self.assertTrue(
                (fitting_problem.data_y[ix][sort] == expected_y_data[ix]).all()
            )
            self.assertTrue(
                (fitting_problem.data_e[ix][sort] == expected_e_data[ix]).all()
            )

        self.options.cost_func_type = ["nlls"]
        fitting_problem.correct_data()
        for ix, sort in enumerate(fitting_problem.sorted_index):
            self.assertTrue(
                (fitting_problem.data_x[ix][sort] == expected_x_data[ix]).all()
            )
            self.assertTrue(
                (fitting_problem.data_y[ix][sort] == expected_y_data[ix]).all()
            )
            self.assertIs(fitting_problem.data_e[ix], None)

    @parameterized.expand(
        [
            (True, [np.array([1, 2]), np.array([3, 4])], ["params", "x"]),
            (False, np.array([1, 2]), ["params"]),
        ]
    )
    @patch("fitbenchmarking.parsing.fitting_problem.FittingProblem.eval_model")
    def test_ini_y_args(self, multifit, data_x, args, mock):
        """
        Tests ini_y calls eval_model using the right args.
        """
        fitting_problem = FittingProblem(self.options)
        fitting_problem.multifit = multifit
        fitting_problem.data_x = data_x
        fitting_problem.starting_values = [{0: "0"}]

        fitting_problem.ini_y()
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(list(mock.call_args[1].keys()), args)
