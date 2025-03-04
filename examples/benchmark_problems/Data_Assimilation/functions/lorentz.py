"""
This file contains the functions required to run lorentz system examples.
"""
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
    if x.ndim == 1:
        return np.array([
            sigma * (x[1] - x[0]),
            r * x[0] - x[1] - x[0] * x[1],
            x[0] * x[1] - b * x[2]
        ])

    raise ValueError('x is the wrong shape in lorentz3d call.')
