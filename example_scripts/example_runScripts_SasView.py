from sasmodels.core import load_model
from sasmodels.bumps_model import Model, Experiment
from sasmodels.data import load_data

from bumps.names import *
from bumps.fitters import fit
from bumps.formatnum import format_uncertainty

import matplotlib.pyplot as plt

import os

current_path = os.path.realpath(__file__)
dir_path = os.path.dirname(current_path)
main_dir = os.path.dirname(dir_path)
oneD_data_dir = os.path.join(main_dir, 'benchmark_problems', '1D_data', 'cyl_400_20.txt')


test_data = load_data(oneD_data_dir)
kernel = load_model('cylinder')

#We set some errors for demonstration
test_data.dy = 0.2*test_data.y

pars = dict(radius=35,
            length=350,
            background=0.0,
            scale=1.0,
            sld=4.0,
            sld_solvent=1.0)
print(pars)
model = Model(kernel, **pars)

# SET THE FITTING PARAMETERS
model.radius.range(1, 50)
model.length.range(1, 500)

M = Experiment(data=test_data, model=model)
problem = FitProblem(M)
print("Initial chisq", problem.chisq_str())
problem.plot()
# pylab.show()
plt.show()

result = fit(problem, method='amoeba')
print("Final chisq", problem.chisq_str())
for k, v, dv in zip(problem.labels(), result.x, result.dx):
    print(k, ":", format_uncertainty(v, dv))
problem.plot()
plt.show()
