
from fitbenchmarking.fitting.software_controllers.base_software import BaseSoftwareController


class MantidController(BaseSoftwareController):

    def __init__(self, problem, use_errors):
        super(MantidController, self).__init__(problem, use_errors)

    def setup(self, minimizer):
        """
        Setup problem ready to run with Mantid.
        """

    def fit(self):
        """
        Run problem with Mantid.
        """

    def result(self):
        """
        Convert the result to a numpy array and return it.
        """
