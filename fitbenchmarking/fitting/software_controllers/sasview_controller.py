
import numpy as np
from bumps.fitters import fit as bumpsFit
from bumps.names import Curve, FitProblem
from sasmodels.data import Data1D

from fitbenchmarking.fitting.software_controllers.base_software_controller import \
    BaseSoftwareController


class SasviewController(BaseSoftwareController):

    def __init__(self, problem, use_errors):
        super(SasviewController, self).__init__(problem, use_errors)

        self.param_names = [param[0] for param in problem.starting_values]

        data_obj = Data1D(x=self.data_x, y=self.data_y, dy=self.data_e)

        self.sas_data = data_obj

    def setup(self):
        """
        Setup problem ready to run with SasView.
        """
        # Bumps fails with the *args notation
        wrapper = "def fitFunction(x, {}):\n".format(', '.join(self.param_names))
        wrapper += "    return func(x, {})".format(', '.join(self.param_names))

        exec_dict = {'func': self.function}
        exec(wrapper, exec_dict)

        model = exec_dict['fitFunction']

        # Remove any function attribute. BinWidth is the only attribute in all FitBenchmark (Mantid) problems.
        param_dict = {name: value
                      for name, value in zip(self.param_names, self.initial_params)}

        # Create a Function Wrapper for the problem function. The type of the Function Wrapper is acceptable by Bumps.
        func_wrapper = Curve(model, x=self.data_x, y=self.data_y, dy=self.data_e, **param_dict)

        # Set a range for each parameter
        for name in self.param_names:
            minVal = -np.inf
            maxVal = np.inf
            func_wrapper.__dict__[name].range(minVal, maxVal)

        # Create a Problem Wrapper. The type of the Problem Wrapper is acceptable by Bumps fitting.
        self.func_wrapper = func_wrapper
        self.fitProblem = FitProblem(func_wrapper)

    def fit(self):
        """
        Run problem with SasView.
        """
        result = bumpsFit(self.fitProblem, method=self.minimizer)

        self.success = result.success
        self.bumps_result = result

    def cleanup(self):
        """
        Convert the result to a numpy array and return it.
        """
        
        self.final_params = self.bumps_result.x
        self.results = self.func_wrapper.theory()
