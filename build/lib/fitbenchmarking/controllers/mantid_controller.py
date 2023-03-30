"""
Implements a controller for the Mantid fitting software.
"""

from mantid import simpleapi as msapi
from mantid.fitfunctions import FunctionFactory, IFunction1D
import numpy as np

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.utils.exceptions import ControllerAttributeError

# pylint: disable=protected-access


class MantidController(Controller):
    """
    Controller for the Mantid fitting software.

    Mantid requires subscribing a custom function in a predefined format,
    so this controller creates that in setup.
    """
    #: A map from fitbenchmarking cost functions to mantid ones.
    COST_FUNCTION_MAP = {
        'nlls': 'Unweighted least squares',
        'weighted_nlls': 'Least squares',
        'poisson': 'Poisson',
    }

    algorithm_check = {
            'all': ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
                    'Conjugate gradient (Polak-Ribiere imp.)',
                    'Damped GaussNewton', 'Levenberg-Marquardt',
                    'Levenberg-MarquardtMD', 'Simplex', 'SteepestDescent',
                    'Trust Region', 'FABADA'],
            'ls': ['Levenberg-Marquardt', 'Levenberg-MarquardtMD',
                   'Trust Region', 'FABADA'],
            'deriv_free': ['Simplex', 'FABADA'],
            'general': ['BFGS', 'Conjugate gradient (Fletcher-Reeves imp.)',
                        'Conjugate gradient (Polak-Ribiere imp.)',
                        'Damped GaussNewton', 'Simplex', 'SteepestDescent'],
            'simplex': ['Simplex'],
            'trust_region': ['Trust Region', 'Levenberg-Marquardt',
                             'Levenberg-MarquardtMD'],
            'levenberg-marquardt': ['Levenberg-Marquardt',
                                    'Levenberg-MarquardtMD'],
            'gauss_newton': ['Damped GaussNewton'],
            'bfgs': ['BFGS'],
            'conjugate_gradient': ['Conjugate gradient (Fletcher-Reeves imp.)',
                                   'Conjugate gradient (Polak-Ribiere imp.)'],
            'steepest_descent': ['SteepestDescent'],
            'global_optimization': ['FABADA']}

    jacobian_enabled_solvers = ['BFGS',
                                'Conjugate gradient (Fletcher-Reeves imp.)',
                                'Conjugate gradient (Polak-Ribiere imp.)',
                                'Damped GaussNewton', 'Levenberg-Marquardt',
                                'Levenberg-MarquardtMD', 'SteepestDescent',
                                'Trust Region']

    def __init__(self, cost_func):
        """
        Setup workspace, cost_function, ignore_invalid, and initialise vars
        used for temporary storage within the mantid controller

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)

        self.support_for_bounds = True

        for fb_cf, mantid_cf in self.COST_FUNCTION_MAP.items():
            if isinstance(self.cost_func, create_cost_func(fb_cf)):
                self._cost_function = mantid_cf
                break
        else:
            raise ControllerAttributeError('Mantid Controller does not support'
                                           ' the requested cost function '
                                           f'{self.cost_func.__class__}')

        self._param_names = self.problem.param_names
        self._status = None

        if self.problem.multifit:
            # Multi Fit
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
            data_obj = msapi.CreateWorkspace(DataX=self.data_x,
                                             DataY=self.data_y,
                                             DataE=self.data_e)
            other_inputs = []
            self._multi_fit = 0

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

            # Add constraints if parameter bounds are set
            if self.value_ranges is not None and self._multi_fit:
                constraints = ','.join('{0} < f{1}.{2} < {3}'.format(
                    self.value_ranges[i][0], j, p, self.value_ranges[i][1])
                    for i, p in enumerate(self._param_names)
                    for j in range(0, self._multi_fit))
                function_def += '; constraints=({})'.format(constraints)
            elif self.value_ranges is not None:

                if ';' not in function_def:
                    self._param_names = [
                        'f0.'+name for name in self._param_names]

                constraints = ','.join('{0} < {1} < {2}'.format(
                    self.value_ranges[i][0], p, self.value_ranges[i][1])
                    for i, p in enumerate(self._param_names))
                function_def += '; constraints=({})'.format(constraints)

            self._mantid_equation = function_def
        except KeyError:
            # This will be completed in setup as it requires initial params
            self._mantid_equation = None

        # Arguments will change if multi-data
        self._added_args = {'InputWorkspace_{}'.format(i + 1): v
                            for i, v in enumerate(other_inputs)}

    def setup(self):
        """
        Setup problem ready to run with Mantid.

        Adds a custom function to Mantid for calling in fit().
        """

        if self._mantid_equation is None:
            start_val_list = ['{0}={1}'.format(name, value)
                              for name, value
                              in zip(self._param_names, self.initial_params)]

            start_val_str = ', '.join(start_val_list)
            function_def = "name=fitFunction, " + start_val_str

            def get_params(ff_self):
                fit_param = np.zeros(len(self._param_names))
                fit_param.setflags(write=1)
                for i, param in enumerate(self._param_names):
                    fit_param[i] = ff_self.getParameterValue(param)
                return fit_param

            # pylint: disable=no-self-argument
            class fitFunction(IFunction1D):
                """
                A wrapper to register a custom function in Mantid.
                """
                def init(ff_self):
                    """
                    Initialiser for the Mantid wrapper.
                    """

                    for i, p in enumerate(self._param_names):
                        ff_self.declareParameter(p)
                        if self.value_ranges is not None:
                            ff_self.addConstraints('{0} < {1} < {2}'.format(
                                self.value_ranges[i][0], p,
                                self.value_ranges[i][1]))

                def function1D(ff_self, xdata):
                    """
                    Pass through for cost-function evaluation.
                    """

                    fit_param = get_params(ff_self)

                    return self.problem.eval_model(x=xdata,
                                                   params=fit_param)

                if not self.cost_func.jacobian.use_default_jac:

                    def functionDeriv1D(ff_self, xvals, jacobian):
                        """
                        Pass through for jacobian evaluation.
                        """
                        fit_param = get_params(ff_self)

                        jac = self.cost_func.jacobian.eval(fit_param)
                        for i, _ in enumerate(xvals):
                            for j in range(len(fit_param)):
                                jacobian.set(i, j, jac[i, j])

            FunctionFactory.subscribe(fitFunction)

            self._mantid_function = function_def
        else:
            self._mantid_function = self._mantid_equation
        # pylint: enable=no-self-argument

    def fit(self):
        """
        Run problem with Mantid.
        """
        minimizer_str = self.minimizer
        if self.minimizer == 'FABADA':
            # The max iterations needs to be larger for FABADA
            # to work; setting to the value in the mantid docs
            minimizer_str += (",Chain Length=100000"
                              ",Steps between values=10"
                              ",Convergence Criteria=0.01")
            self._added_args['MaxIterations'] = 2000000

        fit_result = msapi.Fit(Function=self._mantid_function,
                               CostFunction=self._cost_function,
                               Minimizer=minimizer_str,
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

        final_params_dict = dict(zip(
            self._mantid_results.OutputParameters.column(0),
            self._mantid_results.OutputParameters.column(1)))

        if not self._multi_fit:
            self.final_params = [final_params_dict[key]
                                 for key in self._param_names]
        else:
            self.final_params = [[final_params_dict[f'f{i}.{name}']
                                  for name in self._param_names]
                                 for i in range(self._multi_fit)]

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

            # pylint: disable=super-with-arguments
            return [super(MantidController, self).eval_chisq(p, xi, yi, ei)
                    for p, xi, yi, ei in zip(params, x, y, e)]
        return super().eval_chisq(params, x, y, e)
