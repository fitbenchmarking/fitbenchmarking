"""
Implements a controller for MATLAB Optimization Toolbox
"""

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory
import os
import dill
import matlab.engine

from fitbenchmarking.controllers.base_controller import Controller
from fitbenchmarking.cost_func.cost_func_factory import create_cost_func
from fitbenchmarking.utils.exceptions import CostFuncError

eng = matlab.engine.start_matlab()


class MatlabController(Controller):
    """
    Controller for MATLAB Optimization Toolbox, implementing lsqcurvefit
    """

    def __init__(self, cost_func):
        """
        Initialises variables used for temporary storage.
        :param cost_func: Cost function object selected from options.
        :type cost_func: subclass of
                :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
        """
        super().__init__(cost_func)
        self.initial_params_mat = None
        self.x_data_mat = None
        self.y_data_mat = None
        self._status = None
        self.result = None
        self.algorithm_check = {
            'all': ['levenberg-marquardt', 'trust-region-reflective'],
            'ls': ['levenberg-marquardt', 'trust-region-reflective'],
            'deriv_free': [],
            'general': []}

    def jacobian_information(self):
        """
        DFO cannot use Jacobian information
        """
        has_jacobian = True
        jacobian_free_solvers = []
        return has_jacobian, jacobian_free_solvers

    def setup(self):
        """
        Setup for Matlab fitting
        """
        if not isinstance(self.cost_func, create_cost_func('nlls')):
            raise CostFuncError('Matlab Optimization controller is not '
                                'compatible with the chosen cost function.')


        # Convert initial params into matlab array
        self.initial_params_mat = matlab.double([self.initial_params])
        self.x_data_mat = matlab.double(self.data_x.tolist())
        self.y_data_mat = matlab.double(self.data_y.tolist())
        
        print('size of y data: ')
        print(self.y_data_mat.size)

        # serialize _eval and open within matlab engine
        # so that matlab fitting function can be called
        temp_dir = TemporaryDirectory()
        temp_file = os.path.join(temp_dir.name, 'temp.pickle')
        with open(temp_file, 'wb') as f:
            dill.dump(self._eval, f)
        eng.workspace['temp_file'] = temp_file
        eng.evalc('py_f = py.open(temp_file,"rb")')
        eng.evalc('eval_mat = py.dill.load(py_f)')
        eng.evalc('py_f.close()')

    def _eval(self, p, xdata):

        kwargs = {"x": self.data_x}
        feval = self.problem.eval_model(p, x=self.data_x)

        eng.workspace['feval'] = matlab.double(feval.tolist())
        print('feval size printed in _eval function: ')
        print(eng.workspace['feval'].size)

        #if nargout > 1:
        #    jeval = -self.jacobian.eval(p)
        #    return feval, jeval
    
        return feval

    def fit(self):
        """
        Run problem with Matlab
        """
        # test output of eval function
        eng.workspace['p'] = self.initial_params_mat
        eng.workspace['xdata'] = self.x_data_mat
        out = eng.eval('eval_mat(p, xdata)')
        print('_eval function output: ')
        print(out.size)
        print(out)

        # if self.jacobian.use_default_jac:
        #     eng.workspace['nargout'] = 1
        #     eng.evalc('fun = @(p,xdata)eval_mat(p,xdata,nargout)')
        # else:
        #     eng.workspace['nargout'] = 2
        #     eng.evalc('fun = @(p,xdata)eval_mat(p,xdata,nargout)')    
            
        [self.result, _, exitflag] = eng.lsqcurvefit(
            eng.workspace['eval_mat'], self.initial_params_mat,
            self.x_data_mat, self.y_data_mat, nargout=3)
        self._status = int(exitflag)

    def cleanup(self):
        """
        Convert the result to a numpy array and populate the variables results
        will be read from.
        """
        # todo: check exitflag output for lsqcurvefit
        if self._status == 1:
            self.flag = 0
        elif self._status == 0:
            self.flag = 1
        else:
            self.flag = 2

        self.final_params = self.result[0]