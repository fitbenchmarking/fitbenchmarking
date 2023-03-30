"""
Implements the TimerWithMaxTime class used for checking the
'max_runtime' is not exceeded.
"""
from time import time
from fitbenchmarking.utils.exceptions import MaxRuntimeError


class TimerWithMaxTime:
    """
    A timer class used for checking if the 'max_runtime' is exceeded when
    executing the fits.
    """

    def __init__(self, max_runtime: float):
        """
        Initialise the timer used for checking whether or not the
        'max_runtime' option is exceeded while processing the fits.

        :param max_runtime: The maximum allowed runtime in seconds.
        :type max_runtime: float`
        """
        self.max_runtime: float = max_runtime
        self.total_elapsed_time: float = 0.0
        self.start_time: float = None

    def start(self) -> None:
        """
        Starts the timer by recording the current time.
        """
        self.start_time = time()

    def stop(self) -> None:
        """
        Stops the timer if it is timing something. The elapsed time
        since starting the timer is added onto the total elapsed time.
        """
        if self.start_time is not None:
            self.total_elapsed_time += time() - self.start_time
            self.start_time = None

    def reset(self) -> None:
        """
        Resets the timer so it can be used for timing a different fit
        combination.
        """
        self.total_elapsed_time = 0.0
        self.start_time = None

    def check_elapsed_time(self) -> None:
        """
        Checks whether the max runtime has been exceeded. Raises a
        MaxRuntimeError exception if it has been exceeded. Otherwise,
        it carries on.
        """
        is_timing = self.start_time is not None
        active_elapsed_time = time() - self.start_time if is_timing else 0.0

        if self.total_elapsed_time + active_elapsed_time > self.max_runtime:
            self.stop()
            raise MaxRuntimeError
