import numpy as np


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
    if x.ndim == 1:
        return np.array([x[1], gamma * x[0] + 2 * mu * x[0] ** 3])
    elif x.ndim == 2:
        return np.array([x[:, 1], gamma * x[:, 0] + 2 * mu * x[:, 0] ** 3])
    else:
        raise ValueError("x is the wrong shape in simplified_anac call.")
