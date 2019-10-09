
from fitbenchmarking.fitting.software_controllers.base_software_controller import \
    BaseSoftwareController
from mantid import simpleapi as msapi
from mantid.api import *
from mantid.fitfunctions import *
import numpy as np

class MantidController(BaseSoftwareController):

    def __init__(self, problem, use_errors):
        super(MantidController, self).__init__(problem, use_errors)

        self.param_names = [row[0] for row in problem.starting_values]

        if use_errors:
            self.cost_function = 'Least squares'
        else:
            self.cost_function = 'Unweighted least squares'

        self.ignore_invalid = use_errors & ('WISH17701' not in problem.name)

        data_obj = msapi.CreateWorkspace(DataX=self.data_x,
                                         DataY=self.data_y,
                                         DataE=self.data_e)

        self.mantid_data = data_obj
        self.mantid_function = None
        self.mantid_results = None

    def setup(self):
        """
        Setup problem ready to run with Mantid.
        """
        start_val_list = ['{0}={1}'.format(name, value)
                          for name, value
                          in zip(self.param_names, self.initial_params)]

        start_val_str = ', '.join(start_val_list)
        function_def = "name=fitFunction, " + start_val_str

        class fitFunction(IFunction1D):
            def init(ff_self):

                for param in self.param_names:
                    ff_self.declareParameter(param)

            def function1D(ff_self, xdata):

                fit_param = np.zeros(len(self.param_names))
                fit_param.setflags(write=1)
                for i, param in enumerate(self.param_names):
                    fit_param[i] = ff_self.getParameterValue(param)

                return self.problem.eval_f(xdata, fit_param, self.function_id)

        FunctionFactory.subscribe(fitFunction)

        self.mantid_function = function_def

    def fit(self):
        """
        Run problem with Mantid.
        """
        fit_result = msapi.Fit(Function=self.mantid_function,
                               InputWorkspace=self.mantid_data,
                               Output='ws_fitting_test',
                               Minimizer=self.minimizer,
                               CostFunction=self.cost_function,
                               IgnoreInvalidData=self.ignore_invalid)

        self.mantid_results = fit_result
        self.success = (self.mantid_results.OutputStatus != 'failed')

    def cleanup(self):
        """
        Convert the result to a numpy array and return it.
        """

        if self.mantid_results is not None:
            ws = self.mantid_results.OutputWorkspace
            self.results = ws.readY(1)
            final_params = self.mantid_results.OutputParameters.column(1)
            self.final_params = final_params[:len(self.initial_params)]
        else:
            self.success = False
