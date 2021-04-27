import numpy as np


def lorentz3d(t, x, sigma, r, b):
    """
    Calculates the rhs of a Lorentz system defined by:

    x'[0] = sigma*(x[1]-x[0])
    x'[1] = r*x[0]-x[1]-x[0]*x[2]
    x'[2] = x[0]*x[1]-b*x[2]

    Args:
        t (float): The time to evaluate at
        x (np.ndarray): The x vector (current location)
        sigma (float): The value in the above equations
        r (float): The value in the above equations
        b (float): The value in the above equations
    """
    if len(x.shape) == 1:
        return np.array([
            sigma * (x[1] - x[0]),
            r * x[0] - x[1] - x[0] * x[1],
            x[0] * x[1] - b * x[2]
        ])
    elif len(x.shape) == 2:
        return np.array([
            sigma * (x[:, 1] - x[:, 0]),
            r * x[:, 0] - x[:, 1] - x[:, 0] * x[:, 1],
            x[:, 0] * x[:, 1] - b * x[:, 2]
        ])
    else:
        raise ValueError('x is the wrong shape in lorentz3d call.')


def write_data(fname='data.txt', step=0.1, sigma=10, r=28, b=8/3):
    from scipy.integrate import solve_ivp
    x = np.array([[a/10, b/10, c/10]
                  for a in range(10)
                  for b in range(10)
                  for c in range(10)])

    y = np.zeros_like(x)
    for i, y0 in enumerate(x):
        soln = solve_ivp(fun=lorentz3d,
                         t_span=(0, step),
                         y0=y0,
                         t_eval=[step],
                         args=(sigma, r, b))

        y[i] = soln.y[:, -1]

    with open(fname, 'w') as f:
        f.write('# x0 x1 x2 y0 y1 y2\n')
        for xs, ys in zip(x, y):
            x_str = ' '.join(str(i) for i in xs)
            y_str = ' '.join(str(i) for i in ys)
            f.write(f'{x_str} {y_str}\n')
