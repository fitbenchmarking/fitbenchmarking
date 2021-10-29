"""
Tests for fitbenchmarking.utils.timer.TimerWithMaxTime
"""
from unittest import TestCase
from time import sleep

from fitbenchmarking.utils.exceptions import MaxRuntimeError
from fitbenchmarking.utils.timer import TimerWithMaxTime


class TimerWithMaxTimeTests(TestCase):
    """
    Tests for base software controller class methods.
    """

    def setUp(self):
        self.max_runtime = 60.0
        self.timer = TimerWithMaxTime(self.max_runtime)

    def test_that_start_and_stop_will_record_the_expected_time_elapsed(self):
        """
        Tests that the elapsed time is greater than the sleep time.
        """
        sleep_time = 1.0

        self.timer.start()
        sleep(sleep_time)
        self.timer.stop()

        self.assertGreaterEqual(self.timer.total_elapsed_time, sleep_time)

    def test_that_reset_will_reset_the_total_elapsed_time(self):
        """
        Test the timer data is reset as expected.
        """
        self.timer.total_elapsed_time = 5.5
        self.timer.start_time = 1.2

        self.timer.reset()

        self.assertEqual(self.timer.total_elapsed_time, 0.0)
        self.assertEqual(self.timer.start_time, None)

    def test_that_stop_will_not_raise_even_if_the_timer_is_not_running(self):
        """
        Test that calling stop when the timer is not running will not cause
        any problems.
        """
        self.timer.stop()

    def test_check_elapsed_time_raises_if_the_max_runtime_is_exceeded(self):
        """
        Check the expected MaxRuntimeError exception is raised when
        the max_runtime is exceeded.
        """
        sleep_time = 2.0
        self.max_runtime = 1.0
        self.timer = TimerWithMaxTime(self.max_runtime)

        self.timer.start()
        sleep(sleep_time)

        with self.assertRaises(MaxRuntimeError):
            self.timer.check_elapsed_time()

    def test_check_elapsed_time_will_not_reset_the_timer(self):
        """
        Check the timer is not reset if the max runtime is exceeded. The
        timer should be reset after the exception is caught to ensure
        the MaxRuntime flag is shown for Bumps.
        """
        sleep_time = 2.0
        self.max_runtime = 1.0
        self.timer = TimerWithMaxTime(self.max_runtime)

        self.timer.start()
        sleep(sleep_time)

        with self.assertRaises(MaxRuntimeError):
            self.timer.check_elapsed_time()

        self.assertGreater(self.timer.total_elapsed_time, 0.0)
        self.assertEqual(self.timer.start_time, None)
