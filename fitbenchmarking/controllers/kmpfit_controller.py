"""
Implements a controller for the Kmpfit software.
"""

from kapteyn import kmpfit
from fitbenchmarking.controllers.base_controller import Controller


class KmpfitController(Controller):
    """
    Controller for Kmpfit
    """

    algorithm_check = {
        'all': ['lm-lsqr'],
        'ls': ['lm-lsqr'],
        'deriv_free': [],
        'general': [],
        'simplex': [],
        'trust_region': [],
        'levenberg-marquardt': ['lm-lsqr'],
        'gauss_newton': [],
        'bfgs': [],
        'conjugate_gradient': [],
        'steepest_descent': [],
        'global_optimization': []}

    jacobian_enabled_solvers = ['lm-lsqr']

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.result = None
        self._status = None
        self._popt = None
        self.kmpfit_fitter = kmpfit.Fitter
        self.kmpfit_object = None

    # pylint: disable=unused-argument
    def kmpfit_residuals(self, p, data):
        """
        Residuals for Kmpfit
        """
        return self.cost_func.eval_r(p)

    def kmpfit_jacobians(self, p, data, dflags):
        """
        Jacobians for Kmpfit
        """
        jac = self.cost_func.jac_res(p)
        return jac[0]
    # pylint: enable=unused-argument

    def setup(self):
        """
        Setup problem ready to be run with Kmpfit solver
        """
        self.kmpfit_object = kmpfit.Fitter(residuals=self.kmpfit_residuals,
                                           deriv=self.kmpfit_jacobians,
                                           data=(self.data_x, self.data_y)
                                           )

    def fit(self):
        """
        Run problem with Kmpfit solver
        """

        self.kmpfit_object.fit(params0=self.initial_params)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from
        """
        self._status = self.kmpfit_object.message
        print(self._status)
        if "success" in self._status:
            self.flag = 0
        else:
            self.flag = 2

        self.final_params = self.kmpfit_object.params
