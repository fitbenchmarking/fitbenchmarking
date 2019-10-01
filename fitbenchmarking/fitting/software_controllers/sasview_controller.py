
from fitbenchmarking.fitting.software_controllers.base_software import BaseSoftwareController


class SasviewController(BaseSoftwareController):

    def __init__(self, problem, use_errors):
        super(SasviewController, self).__init__(problem, use_errors)

    def setup(self, minimizer):
        """
        Setup problem ready to run with SasView.
        """

    def fit(self):
        """
        Run problem with SasView.
        """

    def result(self):
        """
        Convert the result to a numpy array and return it.
        """
