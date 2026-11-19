"""
Fit form for the S-parameter time-moment analysis (Eq. 26 of arXiv:2505.08658).
"""

import numpy as np


def sparam_fit_form(x, C_A_plus, C_A_minus, C_V_plus, C_V_minus, m_rho, m_a_1, max_time):
    """
    Two-state staggered fit to the Conserved V-A correlator.

    C(t) = (C_V_plus - (-1)^t * C_A_plus) * (exp(-m_rho*t) + exp(-m_rho*(max_time-t)))
           - (C_A_minus - (-1)^t * C_V_minus) * (exp(-m_a_1*t) + exp(-m_a_1*(max_time-t)))

    Free parameters:
        C_A_plus, C_A_minus, C_V_plus, C_V_minus: amplitude coefficients

    Fixed parameters:
        m_rho:    rho meson mass (lattice units), fixed from previous spectrum
        m_a_1:    a_1 meson mass (lattice units), fixed from previous spectrum
        max_time: temporal extent T = Nt
    """
    return (C_V_plus - (-1) ** x * C_A_plus) * (
        np.exp(-m_rho * x) + np.exp(-m_rho * (max_time - x))
    ) - (C_A_minus - (-1) ** x * C_V_minus) * (
        np.exp(-m_a_1 * x) + np.exp(-m_a_1 * (max_time - x))
    )
