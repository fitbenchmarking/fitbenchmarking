import time
from fitbenchmarking.utils.exceptions import MaxRuntimeError


class TimerWithMaxTime:

    def __init__(self, max_runtime: float):
        """
        Initialise the timer used for checking whether or not the
        'max_runtime' option is exceeded while processing the fits.

        :param max_runtime: The maximum allowed runtime in seconds.
        :type max_runtime: float`
        """
        self._max_runtime: float = max_runtime
        self._total_elapsed_time: float = 0.0
        self._start_time: float = None

    def start(self) -> None:
        """
        Starts the timer by recording the current time.
        """
        self._start_time = time.time()

    def stop(self) -> None:
        """
        Stops the timer if it is timing something. The elapsed time
        since starting the timer is added onto the total elapsed time.
        """
        if self._start_time is not None:
            self._total_elapsed_time += time.time() - self._start_time
            self._start_time = None

    def reset(self) -> None:
        """
        Resets the timer so it can be used for a different fit combination.
        """
        self._total_elapsed_time = 0.0
        self._start_time = None

    def check_elapsed_time(self) -> None:
        """
        Checks whether the max runtime has been exceeded. Raises a MaxRuntimeError
        exception if it has been exceeded. Otherwise, it carries on.
        """
        is_timing = self._start_time is not None

        self.stop()
        if self._total_elapsed_time > self._max_runtime:
            raise MaxRuntimeError

        if is_timing:
            self.start()
