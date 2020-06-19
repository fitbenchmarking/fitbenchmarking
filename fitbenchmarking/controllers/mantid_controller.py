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
        self.algorithm_check = {
            'all': ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex', 'SteepestDescent',
                    'Trust Region'],
            'ls': ['Levenberg-Marquardt', 'Levenberg-MarquardtMD',
                   'Trust Region'],
            'deriv_free': ['Simplex'],
            'general': ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
                        'Conjugate gradient (Polak-Ribiere imp.)',
                        'Damped GaussNewton', 'Simplex', 'SteepestDescent']}

        if self.problem.multifit:
            # Multi Fit
            use_errors = self.data_e[0] is not None
            data_obj = msapi.CreateWorkspace(DataX=self.data_x[0],
                                             DataY=self.data_y[0],
                                             DataE=self.data_e[0],
                                             OutputWorkspace='ws0')
            other_inputs = [
                msapi.CreateWorkspace(DataX=x, DataY=y, DataE=e,
                                      OutputWorkspace='ws{}'.format(i + 1))
                for i, (x, y, e) in enumerate(zip(self.data_x[1:],
                                                  self.data_y[1:],
                                                  self.data_e[1:]))]
            self._multi_fit = len(other_inputs) + 1
        else:
            # Normal Fitting
            use_errors = self.data_e is not None
            data_obj = msapi.CreateWorkspace(DataX=self.data_x,
                                             DataY=self.data_y,
                                             DataE=self.data_e)
            other_inputs = []
            self._multi_fit = 0

        self._cost_function = 'Least squares' if use_errors \
            else 'Unweighted least squares'
        self._mantid_data = data_obj
        self._mantid_function = None
        self._mantid_results = None

        # Use the raw string format if this is from a Mantid problem.
        # This enables advanced features such as contraints.
        try:
            function_def = self.problem.additional_info['mantid_equation']
            if self._multi_fit:
                # Each function must include '$domains=i'
                if ';' in function_def:
                    function_def = ' (composite=CompositeFunction, '\
                                   + 'NumDeriv=false, $domains=i; '\
                                   + '{});'.format(function_def)
                else:
                    function_def += ', $domains=i; '

                # Multi fit must have 'composite=MultiDomainFunction' in the
                # first function.
                composite_str = 'composite=MultiDomainFunction, NumDeriv=1;'
                function_def = composite_str + function_def * self._multi_fit
                ties = ','.join('f{0}.{1}=f0.{1}'.format(i, p)
                                for p in self.problem.additional_info[
                                    'mantid_ties']
                                for i in range(1, self._multi_fit))
                function_def += 'ties=({})'.format(ties)

            self._mantid_function = function_def
        except KeyError:
            # This will be completed in setup as it requires initial params
            self._mantid_function = None

        # Arguments will change if multi-data
        self._added_args = {'InputWorkspace_{}'.format(i + 1): v
                            for i, v in enumerate(other_inputs)}

    def setup(self):
        """
        Setup problem ready to run with Mantid.

        Adds a custom function to Mantid for calling in fit().
        """

        if self._mantid_function is None:
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
                               CostFunction=self._cost_function,
                               Minimizer=self.minimizer,
                               InputWorkspace=self._mantid_data,
                               Output='fit',
                               **self._added_args)

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

        # Mantid gives chi sq as last elem in params
        final_params = self._mantid_results.OutputParameters.column(1)[:-1]
        num_params = len(self.initial_params)
        if self._multi_fit:
            self.final_params = [final_params[i * num_params:(i + 1) * num_params]
                                 for i in range(self._multi_fit)]
        else:
            self.final_params = final_params

    # Override if multi-fit
    # =====================
    def eval_chisq(self, params, x=None, y=None, e=None):
        """
        Computes the chisq value.
        If multi-fit inputs will be lists and this will return a list of chi
        squared of params[i], x[i], y[i], and e[i].

        :param params: The parameters to calculate residuals for
        :type params: list of float or list of list of float
        :param x: x data points, defaults to self.data_x
        :type x: numpy array or list of numpy arrays, optional
        :param y: y data points, defaults to self.data_y
        :type y: numpy array or list of numpy arrays, optional
        :param e: error at each data point, defaults to self.data_e
        :type e: numpy array or list of numpy arrays, optional

        :return: The sum of squares of residuals for the datapoints at the
                 given parameters
        :rtype: numpy array
        """
        if x is not None:
            # If x[0] is scalar this is false, otherwise x is a list of
            # datasets
            multifit = bool(np.shape(x[0]))
        else:
            multifit = self._multi_fit

        if multifit:
            num_inps = len(params)
            if x is None:
                x = [None for _ in range(num_inps)]
            if y is None:
                y = [None for _ in range(num_inps)]
            if e is None:
                e = [None for _ in range(num_inps)]
            return [super(MantidController, self).eval_chisq(p, xi, yi, ei)
                    for p, xi, yi, ei in zip(params, x, y, e)]
        else:
            return super(MantidController, self).eval_chisq(params, x, y, e)
