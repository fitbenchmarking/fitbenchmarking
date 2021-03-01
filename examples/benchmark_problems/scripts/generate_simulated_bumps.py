"""
This script is used to generate simulated count data to fit against based on a
Bumps implementation.
"""


import os

import numpy as np


def peak(x, scale, centre, width, background):
    return scale*np.exp(-0.5*(x-centre)**2/width**2) + background


def write_data(x, y):
    path = f'{os.path.dirname(__file__)}/../data_files'
    with open(f'{path}/simulated_bumps.txt', 'w') as f:
        f.write('# X Y\n')
        lines = [[x[i], y[i]]
                 # if y[i] != 0  # Uncomment to replace 0s with 1s
                 # else [x[i], 1]
                 for i in range(len(x))
                 # if y[i] != 0  # Uncomment to ignore 0 values
                 ]
        f.writelines([f'{i} {j}\n' for i, j in lines])


def write_problem():
    path = f'{os.path.dirname(__file__)}/..'
    with open(f'{path}/simulated_bumps.txt', 'w') as f:
        f.write('# FitBenchmark Problem\n')
        f.write("software = 'Mantid'\n")
        f.write("name = 'Simulated poisson (bumps)'\n")
        f.write("description = 'A simulated dataset for testing poisson cost"
                "functions, based on a simple simulation from bumps.'\n")
        f.write("input_file = 'simulated_bumps.txt'\n")
        f.write("function = 'name=UserFunction,"
                "Formula=scale*exp(-0.5*(x-centre)^2/width^2)+background,"
                "scale=1.0,"
                "centre=2.0,"
                "width=2.0,"
                "background=0.0'\n")


def main():
    x = np.linspace(5, 20, 345)
    # y = np.random.poisson(peak(x, 1000, 12, 1.0, 1))
    # y = np.random.poisson(peak(x, 300, 12, 1.5, 1))
    y = np.random.poisson(peak(x, scale=3, centre=12, width=1.5, background=1))
    write_problem()
    write_data(x, y)


if __name__ == '__main__':
    main()
