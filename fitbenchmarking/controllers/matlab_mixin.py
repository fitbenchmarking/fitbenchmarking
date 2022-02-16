"""
Implements mixin class for the matlab fitting software controllers.
"""

import os
from tempfile import TemporaryDirectory

from fitbenchmarking.utils.exceptions import MissingSoftwareError

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
            raise MissingSoftwareError('Requirements are missing for Matlab '
                                       'fitting, module "dill" is required.')

        self.initial_params_mat = None

    def setup_timer(self, func, eng):
        """
        Create an interface into the timer associated with the named function.
        The timer will be created in the matlab engine as "timer" and must
        not be overridden, although this can be changed in this function if
        there's a conflict.

        This overrides the controller's timer so that it can be controlled from
        other parts of the code.

        :param func: The name of the function to use for timing
                     (from the perspective of the matlab engine).
        :type func: str
        :param eng: The matlab engine for the work
        :type eng: matlab.engine
        """
        eng.evalc(f'timer = py.getattr({func}, "__self__").problem.timer')
        self.timer = MatlabTimerInterface('timer', eng)

    @staticmethod
    def py_to_mat(func, eng):
        """
        Function that serializes a python function and then
        loads it into the Matlab engine workspace
        """
        temp_dir = TemporaryDirectory()
        temp_file = os.path.join(temp_dir.name, 'temp.pickle')
        with open(temp_file, 'wb') as f:
            dill.dump(func, f)
        eng.workspace['temp_file'] = temp_file
        eng.evalc('fp = py.open(temp_file,"rb")')
        eng.evalc('fm = py.dill.load(fp)')
        eng.evalc('fp.close()')
        return eng.workspace['fm']


class MatlabTimerInterface:
    """
    A timer to convert from matlab to the python timer.
    """

    def __init__(self, timer, eng):
        """
        Initialiser for MatlabTimerInterface

        :param timer: The name of the timer in the matlab engine
        :type timer: str
        :param eng: The matlab engine that the timer is in
        :type eng: matlab.engine
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
        return lambda: self.eng.evalc(f'{self.timer}.{value}()')
