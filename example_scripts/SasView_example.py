from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data, empty_data1D, Data1D

from sasmodels.models.broad_peak import Iq

from bumps.names import *
from bumps.fitters import fit
from bumps.formatnum import format_uncertainty

import matplotlib.pyplot as plt

import os

current_path = os.path.realpath(__file__)
dir_path = os.path.dirname(current_path)
main_dir = os.path.dirname(dir_path)
oneD_data_dir = os.path.join(main_dir, 'benchmark_problems', '1D_data', 'data_files', 'cyl_400_20.txt')

test_data = load_data(oneD_data_dir)
test_data.dy = 0.2*test_data.y

# print(type(test_data))

data_1D = Data1D(x=test_data.x, y=test_data.y, dy=test_data.dy)

print(type(data_1D.x))

kernel = load_model('cylinder')

# model_test = load_model('sphere')

# kernel = load_model('broad_peak')
# print(type(test_load))
#We set some errors for demonstration

# x_data = empty_data1D(test_data.x)
# print(x_data.x)
# print(type(x_data))
# print(test_data.qmin)
# print(test_data.y)
# print(type(data_1D))

pars = dict(radius=35,
            length=350,
            background=0.0,
            scale=1.0,
            sld=4.0,
            sld_solvent=1.0)

model = Model(kernel, **pars)
# print(model.parameters())
# model = Model(kernel)

# SET THE FITTING PARAMETERS
model.radius.range(1, 50)
model.length.range(1, 500)

# M = Experiment(data=data_1D, model=model)
M = Experiment(data=test_data, model=model)

param_initial = M.parameters()
radius_initial = param_initial['radius']

problem = FitProblem(M)

print("Initial chisq", problem.chisq_str())
# problem.plot()
# problem.summarize()
# pylab.show()
# plt.show()
result = fit(problem, method='dream')

# print(M.theory())
#
# print(test_data.y)

print("Final chisq", problem.chisq_str())
for k, v, dv in zip(problem.labels(), result.x, result.dx):
    print(k, ":", format_uncertainty(v, dv))


# problem.plot()
# print(model.state())
# print(problem.y)
# plt.show()
# print((M.parameters()))