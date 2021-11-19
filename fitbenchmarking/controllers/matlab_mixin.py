"""
Implements mixin class for the matlab fitting software controllers.
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

from fitbenchmarking.utils.exceptions import MissingSoftwareError


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
