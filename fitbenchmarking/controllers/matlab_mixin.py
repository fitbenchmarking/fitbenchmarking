"""
Implements mixin class for the matlab fitting software controllers.
"""

import os
from tempfile import TemporaryDirectory

from fitbenchmarking.utils.exceptions import (
    IncompatibleProblemError,
    MissingSoftwareError,
)
from fitbenchmarking.utils.matlab_engine import ENG as eng
from fitbenchmarking.utils.matlab_engine import (
    add_persistent_matlab_var,
    clear_non_persistent_matlab_vars,
    list_persistent_matlab_vars,
)

try:
    import dill

    import_success = True
except ImportError:
    import_success = False


# If we re-implement caching, make sure the cache is cleared by the
# matlab controllers to avoid unwanted errors.
class MatlabMixin:
    """
    Mixin class for matlab fitting software controllers
    """

    def __init__(self, cost_func):
        """
        Initialise anything that is needed specifically for matlab
        fitting software
        """
        super().__init__(cost_func)

        if not import_success:
            raise MissingSoftwareError(
                "Requirements are missing for Matlab "
                'fitting, module "dill" is required.'
            )

        self.initial_params_mat = None
        self.original_timer = None
        self.eng = eng
        self.pickle_error = None

        try:
            with TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "temp.pickle")
                with open(temp_file, "wb") as f:
                    dill.dump(cost_func, f)
                self.eng.workspace["temp_file"] = temp_file
                self.eng.evalc('cf_f = py.open(temp_file,"rb")')
                self.eng.evalc("global cf")
                self.eng.evalc("cf = py.dill.load(cf_f)")
                add_persistent_matlab_var("cf")
                self.eng.evalc("cf_f.close()")

                if cost_func.problem.format == "horace":
                    matlab_dump = os.path.join(temp_dir, "dump.mat")
                    to_transfer = list_persistent_matlab_vars()
                    to_transfer_str = "', '".join(
                        v for v in to_transfer if v != "cf"
                    )
                    to_transfer_str = f"'{to_transfer_str}'"
                    self.eng.evalc(
                        f"save('{matlab_dump}', {to_transfer_str});"
                    )
                    print(
                        self.eng.evalc(
                            f"cf.problem.set_persistent_vars('{matlab_dump}')"
                        )
                    )

        except RuntimeError as e:
            self.pickle_error = e

        self.setup_timer()

    def _validate_problem_format(self):
        super()._validate_problem_format()
        if self.pickle_error is not None:
            raise IncompatibleProblemError(
                "Failed to load problem in MATLAB"
            ) from self.pickle_error

    def clear_matlab(self):
        """
        Clear the matlab instance, ready for the next setup.
        """
        clear_non_persistent_matlab_vars()
        self.eng.evalc("global cf")
        self.eng.evalc("global timer")

    def setup_timer(self):
        """
        Create an interface into the timer associated with the cost function.
        The timer will be created in the matlab engine as "timer" and must
        not be overridden, although this can be changed in this function if
        there's a conflict.

        This overrides the controller's timer so that it can be controlled from
        other parts of the code.
        """
        self.eng.evalc("global timer")
        self.eng.evalc("timer = cf.problem.timer")
        add_persistent_matlab_var("timer")
        if self.original_timer is None:
            self.original_timer = self.timer
        self.timer = MatlabTimerInterface("timer")

    def py_to_mat(self, func):
        """
        Get the named function from the matlab version of the cost function

        :param func: The name of the function to retrieve
        :type func: str
        """
        self.eng.evalc(f'fct = py.getattr(cf, "{func}");')
        return self.eng.workspace["fct"]


class MatlabTimerInterface:
    """
    A timer to convert from matlab to the python timer.
    """

    def __init__(self, timer):
        """
        Initialiser for MatlabTimerInterface

        :param timer: The name of the timer in the matlab engine
        :type timer: str
        """
        self.timer = timer
        self.eng = eng

    def __getattr__(self, value):
        """
        Override attribute access to return a deferred function which will be
        done inside matlab when called.

        This will only work if no arguments are passed and no return value is
        required.

        E.g: self.start will become lambda: self.eng.evalc('timer.start()')

        :param value: The name of the attribute to access
        :type value: str
        :return: A function which will call the requested function in matlab
        :rtype: lambda
        """
        return lambda: self.eng.evalc(f"{self.timer}.{value}()")
