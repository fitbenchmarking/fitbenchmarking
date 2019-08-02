from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data, Data1D

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

data_1D = Data1D(x=test_data.x, y=test_data.y)

print(data_1D.x)

kernel = load_model('cylinder')

#We set some errors for demonstration
test_data.dy = 0.2*test_data.y

pars = dict(radius=35,
            length=350,
            background=0.0,
            scale=1.0,
            sld=4.0,
            sld_solvent=1.0)

model = Model(kernel, **pars)
print(model(data_1D.x))

# SET THE FITTING PARAMETERS
model.radius.range(1, 50)
model.length.range(1, 500)

M = Experiment(data=test_data, model=model)


# def line(x, m, b=0):
#     return m*x + b
#
# test_M = Curve(line,test_data.x,test_data.y,m=2,b=2)
# print(type(test_M))

problem = FitProblem(M)

print(type(problem))
print("Initial chisq", problem.chisq_str())
problem.plot()
problem.summarize()
# pylab.show()
# plt.show()

result = fit(problem, method='amoeba')
print(test_data.x)
print(result.x)
print("Final chisq", problem.chisq_str())
for k, v, dv in zip(problem.labels(), result.x, result.dx):
    print(k, ":", format_uncertainty(v, dv))
problem.plot()
# print(problem.y)
# plt.show()
