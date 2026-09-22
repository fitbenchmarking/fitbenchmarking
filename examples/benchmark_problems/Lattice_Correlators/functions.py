"""
Model functions for Lattice_Correlators benchmark problems.
"""

import numpy as np


def periodic_cosh(x, a, E, Nt):
    """
    Periodic single-cosh model for correlator plateau fits.

    C(t) = a^2 * (exp(-E*t) + exp(-E*(Nt - t)))

    Parameters:
        a: overlap amplitude
        E: ground-state mass (in lattice units)
        Nt: temporal lattice extent

    """
    return a**2 * (np.exp(-E * x) + np.exp(-E * (Nt - x)))
