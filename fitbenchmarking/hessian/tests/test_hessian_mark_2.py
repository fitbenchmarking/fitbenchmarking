"""
Unit testing for the hessian directory.
"""
from unittest import TestCase

import numpy as np
import math

from fitbenchmarking.cost_func.nlls_cost_func import NLLSCostFunc
from fitbenchmarking.cost_func.weighted_nlls_cost_func import\
    WeightedNLLSCostFunc
from fitbenchmarking.cost_func.hellinger_nlls_cost_func import\
    HellingerNLLSCostFunc
from fitbenchmarking.cost_func.poisson_cost_func import\
    PoissonCostFunc
from fitbenchmarking.hessian.analytic_hessian import Analytic
from fitbenchmarking.jacobian.analytic_jacobian import Analytic\
    as JacobianClass
from fitbenchmarking.hessian.hessian_factory import create_hessian
from fitbenchmarking.parsing.fitting_problem import FittingProblem
from fitbenchmarking.utils import exceptions
from fitbenchmarking.utils.options import Options


def f_ls(x,p1,p2):
    return (x*(p1+p2)**2)**2

def J_ls(x,p):
    return np.column_stack((4*x**2*(p[0]+p[1])**3,
                            4*x**2*(p[0]+p[1])**3))

def H_ls(x,p):
    return np.array([[12*x**2*(p[0]+p[1])**3, 12*x**2*(p[0]+p[1])**3],
             [12*x**2*(p[0]+p[1])**3, 12*x**2*(p[0]+p[1])**3],])

def r_nlls(x,y,p1,p2):
    return y - f_ls(x,p1,p2)

def grad2_r_nlls(x,p):
    return np.array([[12*x**2*(p[0]+p[1])**3, 12*x**2*(p[0]+p[1])**3],
             [12*x**2*(p[0]+p[1])**3, 12*x**2*(p[0]+p[1])**3],])

def r_weighted_nlls(x,y,e,p1,p2):
    return (y - f_ls(x,p1,p2))/e

def grad2_r_weighted_nlls(x,e,p):
    return np.array([[12*x**2*(p[0]+p[1])**3/e, 12*x**2*(p[0]+p[1])**3/e],
             [12*x**2*(p[0]+p[1])**3/e, 12*x**2*(p[0]+p[1])**3/e],])

def r_hellinger(x,y,p1,p2):
    return np.sqrt(y) - np.sqrt(f_ls(x,p1,p2))

def grad2_r_hellinger(x, p):
    return np.array([[2*x, 2*x],[2*x, 2*x],])

def f_poisson(x,p1,p2):
    return np.exp((x*(p1+p2)))

def r_poisson(x,y,p1,p2):
    return (y*(np.log(y)-np.log(f_poisson(x,p1,p2)))-(y-f_poisson(x,p1,p2)))

def grad2_r_poisson(x,p):
    return np.array([[x**2*np.exp((x*(p[0]+p[1]))), x**2*np.exp((x*(p[0]+p[1])))],
                    [x**2*np.exp((x*(p[0]+p[1]))), x**2*np.exp((x*(p[0]+p[1])))],])

def J_poisson(x,p):
    return np.column_stack((x*np.exp(x*(p[0]+p[1])),
                            x*np.exp(x*(p[0]+p[1]))))

def H_poisson(x,p):
    return np.array([[x**2*np.exp((x*(p[0]+p[1]))), x**2*np.exp((x*(p[0]+p[1])))],
                    [x**2*np.exp((x*(p[0]+p[1]))), x**2*np.exp((x*(p[0]+p[1])))],])


class Test2HessianClass(TestCase):
    """
    Tests for Hessian classes
    """

    def setUp(self):
        """
        Setting up tests
        """
        options = Options()
        self.fitting_problem = FittingProblem(options)
        options.cost_func_type = "nlls"
        self.fitting_problem = FittingProblem(options)
        self.fitting_problem.data_x = np.array([1, 2, 3, 4, 5])
        self.fitting_problem.data_y = np.array([1, 2, 4, 8, 16])
        self.params = [6, 0.1]

    def test2_nlls(self):
        self.fitting_problem.options.cost_func_type = "nlls"
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.cost_func = NLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        print('eval')
        print(eval_result)
        actual_hessian = np.sum(r_nlls(self.fitting_problem.data_x, self.fitting_problem.data_y,
                                self.params[0], self.params[1])*grad2_r_nlls(self.fitting_problem.data_x, self.params),2)
        print('actual')
        print(actual_hessian)
        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test2_weighted_nlls(self):
        self.fitting_problem.options.cost_func_type = "weighted_nlls"
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        e = np.array([1, 2, 1, 3, 1])
        self.fitting_problem.data_e = e
        self.cost_func = WeightedNLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        print('eval')
        print(eval_result)
        actual_hessian = np.sum(r_weighted_nlls(self.fitting_problem.data_x, self.fitting_problem.data_y, e,
                                self.params[0], self.params[1])*grad2_r_weighted_nlls(self.fitting_problem.data_x, e, self.params),2)
        print('actual')
        print(actual_hessian)
        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test2_hellinger(self):
        self.fitting_problem.options.cost_func_type = "hellinger_nlls"
        self.fitting_problem.function = f_ls
        self.fitting_problem.jacobian = J_ls
        self.fitting_problem.hessian = H_ls
        self.cost_func = HellingerNLLSCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        print('eval')
        print(eval_result)
        actual_hessian = np.sum(r_hellinger(self.fitting_problem.data_x, self.fitting_problem.data_y,
                                self.params[0], self.params[1])*grad2_r_hellinger(self.fitting_problem.data_x, self.params),2)
        print('actual')
        print(actual_hessian)
        self.assertTrue(np.isclose(actual_hessian, eval_result).all())

    def test2_poisson(self):
        self.fitting_problem.options.cost_func_type = "poisson"
        self.fitting_problem.function = f_poisson
        self.fitting_problem.jacobian = J_poisson
        self.fitting_problem.hessian = H_poisson
        self.cost_func = PoissonCostFunc(self.fitting_problem)
        self.jacobian = JacobianClass(self.cost_func)
        hes = Analytic(self.cost_func, self.jacobian)
        eval_result, _ = hes.eval(params=self.params)
        print('eval p')
        print(eval_result)
        actual_hessian = np.sum(r_poisson(self.fitting_problem.data_x, self.fitting_problem.data_y,
                                self.params[0], self.params[1])*grad2_r_poisson(self.fitting_problem.data_x, self.params),2)
        print('actual p')
        print(actual_hessian)
        self.assertTrue(np.isclose(actual_hessian, eval_result).all())
