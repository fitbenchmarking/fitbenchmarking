"""
This file contains the functions required to run the simplified anac system
examples.
"""
import numpy as np


# pylint: disable=unused-argument
def simplified_anac(t, x, gamma, mu):
    """
    Calculates the rhs of the system defined by:

    x'[0] = x[1]
    x'[1] = gamma*x[0]+2*mu*x[0]^3

    Args:
        t (float): The time to evaluate at
        x (np.ndarray): The x vector (current location)
        gamma (float): The value in the above equations
        mu (float): The value in the above equations
    """
    if len(x.shape) == 1:
        return np.array([
            x[1],
            gamma * x[0] + 2 * mu * x[0]**3
        ])

    raise ValueError('x is the wrong shape in simplified_anac call.')
