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


import matlab.engine

eng = matlab.engine.start_matlab()


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
        self.old_timer = None
        self.eng = eng
        if not import_success:
            raise MissingSoftwareError('Requirements are missing for Matlab '
                                       'fitting, module "dill" is required.')

        self.initial_params_mat = None

    def clear_matlab(self):
        """
        Clear the matlab instance, ready for the next setup.

        This should be called at the end of self.cleanup()
        """
        self.eng.clear('all', nargout=0)
        if self.old_timer is not None:
            self.timer = self.old_timer
            self.old_timer = None

    def setup_timer(self, func):
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
        """
        self.eng.evalc(f'timer = py.getattr({func}, "__self__").problem.timer')
        self.old_timer = self.timer
        self.timer = MatlabTimerInterface('timer')

    def py_to_mat(self, func):
        """
        Function that serializes a python function and then
        loads it into the Matlab engine workspace
        """
        with TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, 'temp.pickle')
            with open(temp_file, 'wb') as f:
                dill.dump(func, f)
            self.eng.workspace['temp_file'] = temp_file
            self.eng.evalc('fp = py.open(temp_file,"rb")')
            self.eng.evalc('fm = py.dill.load(fp)')
            self.eng.evalc('fp.close()')
        return self.eng.workspace['fm']


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
        return lambda: self.eng.evalc(f'{self.timer}.{value}()')
