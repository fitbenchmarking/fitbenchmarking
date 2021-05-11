"""
This function was used to generate data for the data assimilation directory.
"""

import numpy as np
from scipy.integrate import solve_ivp


def write_data(fun, args, fname='data.txt', step=0.1, sd=0.1):
    out = fun(0, np.zeros((10)), *args)
    dim = len(out)
    tmp_x = [[i/10] for i in range(10)]
    for _ in range(dim-1):
        tmp_x = [a + [i/10]
                 for a in tmp_x
                 for i in range(10)]
    x = np.array(tmp_x)

    exact_y = np.zeros_like(x)
    for i, y0 in enumerate(x):
        soln = solve_ivp(fun=fun,
                         t_span=(0, step),
                         y0=y0,
                         t_eval=[step],
                         args=args)

        exact_y[i] = soln.y[:, -1]

    noisy_y = exact_y + np.random.normal(loc=0, scale=sd, size=exact_y.shape)

    x_header = ' '.join(["x" + str(i) for i in range(dim)])
    y_header = ' '.join(["y" + str(i) for i in range(dim)])
    header = f'# {x_header} {y_header}\n'
    for name, y in zip([fname, 'noisy_' + fname], [exact_y, noisy_y]):
        with open(name, 'w') as f:
            f.write(header)
            for xs, ys in zip(x, y):
                x_str = ' '.join(str(i) for i in xs)
                y_str = ' '.join(str(i) for i in ys)
                f.write(f'{x_str} {y_str}\n')
