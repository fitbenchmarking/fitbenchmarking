"""
Implements a controller for MATLAB Curve Fitting Toolbox
"""

import os

import matlab

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.controllers.matlab_mixin import MatlabMixin


class MatlabCurveController(MatlabMixin, Controller):
    """
    Controller for MATLAB Curve Fitting Toolbox fitting (fit)
    """

    algorithm_check = {
        "all": ["Trust-Region", "Levenberg-Marquardt"],
        "ls": ["Trust-Region", "Levenberg-Marquardt"],
        "deriv_free": [],
        "general": [],
        "simplex": [],
        "trust_region": ["Trust-Region", "Levenberg-Marquardt"],
        "levenberg-marquardt": ["Levenberg-Marquardt"],
        "gauss_newton": [],
        "bfgs": [],
        "conjugate_gradient": [],
        "steepest_descent": [],
        "global_optimization": [],
        "MCMC": [],
    }

    incompatible_problems = ["mantid", "horace"]
    controller_name = "matlab_curve"

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.

        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.support_for_bounds = True
        self.options = None
        self._status = None
        self.result = None

    def setup(self):
        """
        Setup for Matlab fitting
        """
        # Convert initial params into matlab array
        self.initial_params_mat = matlab.double(list(self.initial_params))
        self.eng.workspace["x_data"] = matlab.double(self.data_x.tolist())
        self.eng.workspace["y_data"] = matlab.double(self.data_y.tolist())

        self.eng.evalc("global e_data")
        if self.data_e is not None:
            self.eng.workspace["e_data"] = matlab.double(self.data_e.tolist())
        else:
            self.eng.workspace["e_data"] = matlab.double([])

        eval_path = os.path.join(
            os.path.dirname(__file__), "matlab_curve_controller"
        )
        self.eng.addpath(eval_path)

        if self.value_ranges is not None:
            lb, ub = zip(*self.value_ranges)
            self.eng.workspace["lower_bounds"] = matlab.double(lb)
            self.eng.workspace["upper_bounds"] = matlab.double(ub)
        else:
            # if no bounds are set, then pass empty arrays to
            # fitoptions function
            self.eng.workspace["lower_bounds"] = matlab.double([])
            self.eng.workspace["upper_bounds"] = matlab.double([])

        params = self.problem.param_names
        self.eng.workspace["init_params"] = self.initial_params_mat
        self.eng.evalc(
            "opts = fitoptions('StartPoint', init_params,"
            "'Method', 'NonLinearLeastSquares',"
            f"'Algorithm', '{self.minimizer}',"
            "'Lower', lower_bounds,"
            "'Upper', upper_bounds)"
        )

        self.eng.evalc(
            f"ft = fittype(@({', '.join(params)}, x, y)"
            f"double(eval_r(x, y, {', '.join(params)}))',"
            "'options', opts, 'independent', {'x', 'y'},"
            "'dependent', 'z')"
        )

    def fit(self):
        """
        Run problem with Matlab
        """
        self.eng.evalc(
            """[fitobj, gof, output] = fit([x_data', y_data'],
            zeros(size(x_data))', ft);"""
        )
        self._status = int(self.eng.workspace["output"]["exitflag"])

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        if self._status == 1:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self.eng.coeffvalues(self.eng.workspace["fitobj"])[
            0
        ]
