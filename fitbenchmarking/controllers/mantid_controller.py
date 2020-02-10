"""
Implements a controller for the Mantid fitting software.
"""

from mantid import simpleapi as msapi
from mantid.fitfunctions import FunctionFactory, FunctionWrapper, IFunction1D
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller


class MantidController(Controller):
    """
    Controller for the Mantid fitting software.

    Mantid requires subscribing a custom function in a predefined format,
    so this controller creates that in setup.
    """

    def __init__(self, problem):
        """
        Setup workspace, cost_function, ignore_invalid, and initialise vars
        used for temporary storage within the mantid controller

        :param problem: Problem to fit
        :type problem: FittingProblem
        """
        super(MantidController, self).__init__(problem)

        self._param_names = self.problem.param_names

        self._cost_function = 'Least squares' if self.data_e is not None \
            else 'Unweighted least squares'

        data_obj = msapi.CreateWorkspace(DataX=self.data_x,
                                         DataY=self.data_y,
                                         DataE=self.data_e)

        self._mantid_data = data_obj
        self._mantid_function = None
        self._mantid_results = None

    def setup(self):
        """
        Setup problem ready to run with Mantid.

        Adds a custom function to Mantid for calling in fit().
        """
        if isinstance(self.problem.function, FunctionWrapper):
            function_def = self.problem.function
        else:
            start_val_list = ['{0}={1}'.format(name, value)
                              for name, value
                              in zip(self._param_names, self.initial_params)]

            start_val_str = ', '.join(start_val_list)
            function_def = "name=fitFunction, " + start_val_str

            class fitFunction(IFunction1D):
                def init(ff_self):

                    for param in self._param_names:
                        ff_self.declareParameter(param)

                def function1D(ff_self, xdata):

                    fit_param = np.zeros(len(self._param_names))
                    fit_param.setflags(write=1)
                    for i, param in enumerate(self._param_names):
                        fit_param[i] = ff_self.getParameterValue(param)

                    return self.problem.eval_f(x=xdata,
                                               params=fit_param)

            FunctionFactory.subscribe(fitFunction)

        self._mantid_function = function_def

    def fit(self):
        """
        Run problem with Mantid.
        """
        fit_result = msapi.Fit(Function=self._mantid_function,
                               InputWorkspace=self._mantid_data,
                               Output='ws_fitting_test',
                               Minimizer=self.minimizer,
                               CostFunction=self._cost_function)

        self._mantid_results = fit_result
        self._status = self._mantid_results.OutputStatus

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == "success":
            self.flag = 0
        elif "Failed to converge" in self._status:
            self.flag = 1
        else:
            self.flag = 2

        ws = self._mantid_results.OutputWorkspace
        self.results = ws.readY(1)
        final_params = self._mantid_results.OutputParameters.column(1)
        self.final_params = final_params[:len(self.initial_params)]
