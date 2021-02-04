# This script is used to generate simulated poisson data based on a Mantid
# script

import os

import numpy


def VariableStatsData(N, A0, omega, phi, sigma, bg):
    x = numpy.linspace(start=0.0, stop=32.0, num=2001)
    y = (1+A0*numpy.cos(omega*x+phi)*numpy.exp(-(sigma*x)**2)) * \
        numpy.exp(-x/2.197)+bg
    NN = N/numpy.sum(y)  # normalisation so whole spectrum has ~N counts
    return (x, numpy.random.poisson(y*NN))


def write_data(x, y):
    path = f'{os.path.dirname(__file__)}/../data_files'
    with open(f'{path}/simulated_mantid.txt', 'w') as f:
        f.write('# X Y\n')
        lines = [[x[i], y[i]]
                 # if y[i] != 0  # Uncomment to replace 0s with 1s
                 # else [x[i], 1]
                 for i in range(len(x))
                 # if y[i] != 0  # Uncomment to ignore 0 values
                 ]
        f.writelines([f'{i} {j}\n' for i, j in lines])


def write_problem(N):
    path = f'{os.path.dirname(__file__)}/..'
    with open(f'{path}/simulated_mantid.txt', 'w') as f:
        f.write('# FitBenchmark Problem\n')
        f.write("software = 'Mantid'\n")
        f.write("name = 'Simulated poisson (Mantid)'\n")
        f.write("description = 'A simulated dataset for testing poisson cost"
                "functions, based on a simple simulation from Mantid.'\n")
        f.write("input_file = 'simulated_mantid.txt'\n")
        f.write("function = 'name=UserFunction,"
                "Formula=N*((1+A*cos(omega*x+phi)*exp(-(sigma*x)^2))*"
                "exp(-x/2.197)+bg),"
                f"N={0.007*N},"
                "A=0.3,"
                "omega=0.9,"
                "phi=0.2,"
                "sigma=0.12,"
                "bg=0.001'\n")


if __name__ == '__main__':
    args = {'N': 1000,
            'A0': 0.25,
            'omega': 1.0,
            'phi': 0.1,
            'sigma': 0.1,
            'bg': 1.E-4}
    x, y = VariableStatsData(**args)
    write_data(x, y)
    write_problem(N=args['N'])
