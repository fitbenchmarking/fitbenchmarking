"""
Implements base class for the matlab fitting software controllers.
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
try:
    import dill
    import_success = True
except ImportError:
    import_success = False

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.utils.exceptions import MissingSoftwareError


class BaseMatlabController(Controller):
    """
    Base class for matlab fitting software controllers
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

    def setup(self):
        raise NotImplementedError

    def jacobian_information(self):
        raise NotImplementedError

    def fit(self):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def py_to_mat(self, func, eng):
        """
        Function that serializes a python function and then
        loads it into the Matlab engine workspace
        """
        temp_dir = TemporaryDirectory()
        temp_file = os.path.join(temp_dir.name, 'temp.pickle')
        with open(temp_file, 'wb') as f:
            dill.dump(func, f)
        eng.workspace['temp_file'] = temp_file
        eng.evalc('py_f = py.open(temp_file,"rb")')
        eng.evalc('func_mat = py.dill.load(py_f)')
        eng.evalc('py_f.close()')

        return eng.workspace['func_mat']

    def _feval(self, p):
        """
        Function to call from matlab which evaluates the residuals
        """
        feval = -self.cost_func.eval_r(p)
        return feval

    def _jeval(self, p):
        """
        Function to call from matlab which evaluates the jacobian
        """
        jeval = -self.jacobian.eval(p)
        return jeval
