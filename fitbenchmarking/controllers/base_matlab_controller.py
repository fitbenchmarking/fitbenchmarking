"""
Implements base class for the matlab fitting software controllers.
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
import dill

from fitbenchmarking.controllers.base_controller import Controller


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
