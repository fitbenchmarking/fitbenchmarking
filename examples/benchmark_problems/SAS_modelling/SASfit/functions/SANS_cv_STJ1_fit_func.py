"""
Model for the SANS contrast variation problem SANS_cv_STJ1.

This reproduces the global fit stored in ``sas_project_file.txt``: a lognormal
distribution of linear shell particles with a hard sphere structure factor and
a flat background, fitted simultaneously to a series of datasets which differ
only in the scattering length density of the solvent.

For each dataset the scattering intensity is built from three SASfit functions
using the decoupling approach (``SQ,how = 1`` in the project file)::

    I(q) = <|F(q,R)|^2> + <F(q,R)>^2 / N * (S(q) - 1) + P(q)

where ``<.>`` denotes the integral over the LogNorm size distribution of the
core radius ``R``, ``F`` is the LinShell scattering amplitude, ``S`` is the
3D Hard Sphere (GH) structure factor and ``P`` is the polynom form factor.

Every dataset of the series is described by the same ``fit_function``. What
differs between them is the solvent scattering length density ``eta_solv``,
which is fixed by the experiment, and the flat background ``p0``, which SASfit
fits separately for each dataset (the ``c_0`` of scattering contributions 10 to
18 of the project file, which carry no ``P`` label and so are local). The
parameters of the particle itself are shared by the whole series ("global" in
SASfit, ``P1`` to ``P10``).

Which parameters are fitted, and the value each of them starts from, is set
in the ``function`` entry of the problem definition file, the same way it is
for a fit built out of SASfit plugins. Parameters listed in ``fixed_params``
instead are held at the value given there, one set of them per dataset, which
is how each dataset of the series gets its own ``eta_solv``. Tying the shared
parameters together across the datasets, so that the whole series is one
global fit, is left to the ``ties`` entry.

Note that the scattering amplitude is taken from ``sasfit_ff_Kshlin`` rather
than from ``sasfit_ff_LinShell``. The two are the same form factor:
``sasfit_ff_LinShell`` simply returns ``sasfit_ff_Kshlin`` squared. The
decoupling approach needs ``<F>`` and ``<|F|^2>`` separately, so it has to
integrate the amplitude itself, which only Kshlin exposes. Squaring the
amplitude at each point of the size distribution reproduces LinShell exactly.
"""

import ctypes
from os import environ, path

import numpy as np

from fitbenchmarking.parsing.SASStudio_functions import (
    MAXPAR,
    sasfit_plugin_parameters_types,
)

SASLIB_PATH = environ["SASFIT_LOCATION"]
PLUGIN_PATH = path.join(SASLIB_PATH, "plugins")

# LinShell shares its implementation with the Kshlin scattering amplitude and
# uses kernelSelector to pick which of the two radius conventions to use.
# KSHLIN1 takes p[0] as the core radius, which is what SASfit uses for the
# "LinShell" form factor. See sasfit_common/include/sasfit_function.h.
KSHLIN1 = 28

# fraction of the size distribution left outside the integration range,
# n_percent in src/sasfit_old/sasfit.c
N_PERCENT = 0.0001

# The integration range is chosen to hold this moment of the size distribution
# rather than the distribution itself, so that the range is wide enough for the
# R^6 weighting the scattering intensity gives it. SASfit asks
# find_integration_range for moment 6 everywhere it calculates an intensity,
# see src/sasfit_old/sasfit.c.
SD_MOMENT = 6

# Number of Gauss-Legendre nodes used for the size distribution integral.
# The integral is converged to machine precision by 128 nodes over the q
# range of this problem.
N_QUAD = 128

# Value returned for every data point when the parameters are outside the
# domain the SASfit library can be called with. Large enough to be a bad fit,
# small enough to keep the residuals finite for the minimizer.
OUT_OF_DOMAIN = 1.0e8

_libsasfit = ctypes.CDLL(path.join(SASLIB_PATH, "libsasfit.so"))
_libhardspheres = ctypes.CDLL(
    path.join(PLUGIN_PATH, "libsasfit_hard_spheres.so")
)
_libpolynom = ctypes.CDLL(path.join(PLUGIN_PATH, "libsasfit_polynom.so"))

for _lib, _name in [
    (_libsasfit, "sasfit_sd_LogNorm"),
    (_libsasfit, "sasfit_ff_Kshlin"),
    (_libhardspheres, "sasfit_sq_hard_sphere__gh_"),
    (_libpolynom, "sasfit_ff_polynom"),
]:
    _func = getattr(_lib, _name)
    _func.argtypes = [
        ctypes.c_double,
        ctypes.POINTER(sasfit_plugin_parameters_types),
    ]
    _func.restype = ctypes.c_double

_sd_lognorm = _libsasfit.sasfit_sd_LogNorm
_ff_kshlin = _libsasfit.sasfit_ff_Kshlin
_sq_hard_sphere_gh = _libhardspheres.sasfit_sq_hard_sphere__gh_
_ff_polynom = _libpolynom.sasfit_ff_polynom


# Parameters which SASfit holds fixed for this fit. The names in brackets are
# the global parameter labels used in sas_project_file.txt.
P_EXPONENT = 1.0  # LogNorm exponent p                     (P3)
ETA_SH = -2.18146e09  # LinShell shell SLD, eta_sh         (P7)
ETA_HS = 0.05  # hard sphere volume fraction, eta          (P10)
R_HS_FACTOR = 1.075  # hard sphere radius R = 1.075 * mu   (P4)

# The polynom form factor is a degree four polynomial in q,
# p0 + p1*q + p2*q^2 + p3*q^3 + p4*q^4, see plugins/polynom/sasfit_ff_polynom.c
# Any of p0 to p4 which the problem definition file does not name are held at
# zero, so a flat background is just p0.
POLYNOM_MAXPAR = 5

# The values of N, eta_core and eta_solv differ by nearly forty orders of
# magnitude, which collapses the trust region of a least squares minimizer on
# its first step. They are therefore given in the natural units below and
# converted back to SASfit units before the library is called, so that every
# parameter of the fit function is of order one.
PARAMETER_SCALES = {
    "N": 1.0e-28,
    "eta_core": 1.0e10,
    "eta_solv": 1.0e10,
}

equation = "LogNorm x LinShell x 3D Hard Sphere (GH) + polynom"

# nodes and weights of the size distribution integral, on [-1, 1]. They do not
# depend on the parameters, so they are only built once.
_NODES, _WEIGHTS = np.polynomial.legendre.leggauss(N_QUAD)


def _make_param(values, kernel_selector=0):
    """
    Build a SASfit parameter struct holding the given parameter values.

    :param values: The parameter values, in the order SASfit expects them
    :type values: sequence of float
    :param kernel_selector: The SASfit kernelSelector value, if the function
                            needs one
    :type kernel_selector: int
    :return: The parameter struct
    :rtype: sasfit_plugin_parameters_types
    """
    param = sasfit_plugin_parameters_types()
    param.p = (ctypes.c_double * MAXPAR)(*values)
    param.kernelSelector = kernel_selector
    return param


def _integration_range(mu, s):
    """
    The upper limit SASfit uses for the LogNorm size distribution integral,
    chosen so that only N_PERCENT of the SD_MOMENT'th moment of the
    distribution falls outside it. The lower limit is always zero. See
    find_integration_range in src/sasfit_old/sasfit.c.

    :param mu: The median of the LogNorm distribution
    :type mu: float
    :param s: The width of the LogNorm distribution
    :type s: float
    :return: The largest radius to integrate to
    :rtype: float
    """
    return abs(mu) * np.exp(
        -s * s * (P_EXPONENT - SD_MOMENT)
        + np.sqrt(2.0 * s * s * np.log(100.0 / N_PERCENT))
    )


def _is_in_domain(n_mean, s, mu, d_r):
    """
    Check that the parameters are ones the SASfit library can be called with.

    Some of the SASfit functions segfault rather than return an error for
    unphysical parameters (``sasfit_sq_hard_sphere__gh_`` does this for a
    negative radius), which would take the whole fit down with them, so the
    model refuses to call into the library outside of the physical domain.

    :param n_mean: The LogNorm amplitude
    :type n_mean: float
    :param s: The LogNorm width
    :type s: float
    :param mu: The LogNorm median core radius
    :type mu: float
    :param d_r: The shell thickness
    :type d_r: float
    :return: True if the library may be called with these parameters
    :rtype: bool
    """
    values = (n_mean, s, mu, d_r)
    if not all(np.isfinite(v) for v in values):
        return False
    # a size distribution needs a positive width and median, the structure
    # factor needs a positive radius (R = R_HS_FACTOR * mu) and a shell
    # cannot have a negative thickness
    return s > 0.0 and mu > 0.0 and d_r >= 0.0 and n_mean != 0.0


def _polynom_values(coefficients):
    """
    Order the polynom coefficients named in the problem definition file into
    the array SASfit expects. Any which are not named are held at zero.

    :param coefficients: The named coefficients, p0 to p4
    :type coefficients: dict[str, float]
    :raises ValueError: If a coefficient is not one of p0 to p4
    :return: The value of each of the POLYNOM_MAXPAR coefficients
    :rtype: list of float
    """
    values = [0.0] * POLYNOM_MAXPAR
    for name, value in coefficients.items():
        index = name[1:]
        if not (name.startswith("p") and index.isdigit()):
            raise ValueError(f"'{name}' is not a parameter of this model.")
        if int(index) >= POLYNOM_MAXPAR:
            raise ValueError(
                f"'{name}' is beyond the degree of the polynom background, "
                f"which only has p0 to p{POLYNOM_MAXPAR - 1}."
            )
        values[int(index)] = value
    return values


def fit_function(x, N, s, mu, dR, eta_core, x_solv, eta_solv, **coefficients):
    """
    The scattering intensity of one dataset of the series.

    The same function describes every dataset; which dataset it is evaluating
    is decided by the value of the eta_solv parameter, which the problem
    definition file fixes to its own value for each of them.

    The parameters are passed by name, so the order they are given in the
    problem definition file does not matter, and whether one of them is
    fitted or held in 'fixed_params' makes no difference here.

    :param x: The q values to evaluate the intensity at
    :type x: float or np.ndarray
    :param N: The LogNorm amplitude, divided by PARAMETER_SCALES['N']
    :type N: float
    :param s: The LogNorm width
    :type s: float
    :param mu: The LogNorm median core radius
    :type mu: float
    :param dR: The LinShell shell thickness
    :type dR: float
    :param eta_core: The core SLD, divided by PARAMETER_SCALES['eta_core']
    :type eta_core: float
    :param x_solv: The LinShell x_in_solv, which is also its x_out_solv
    :type x_solv: float
    :param eta_solv: The solvent SLD, divided by
                     PARAMETER_SCALES['eta_solv']
    :type eta_solv: float
    :param coefficients: The polynom background coefficients, p0 to p4. Any
                         which are not given are held at zero.
    :type coefficients: float
    :raises ValueError: If a coefficient is not one of p0 to p4
    :return: The scattering intensity at each of the q values
    :rtype: np.ndarray
    """
    q_values = np.atleast_1d(np.asarray(x, dtype=np.float64))
    polynom_values = _polynom_values(coefficients)

    # back into the units the SASfit library expects
    n_mean = N * PARAMETER_SCALES["N"]
    eta_core = eta_core * PARAMETER_SCALES["eta_core"]
    eta_solv = eta_solv * PARAMETER_SCALES["eta_solv"]

    if not _is_in_domain(n_mean, s, mu, dR):
        # steer the minimizer back into the domain rather than calling into
        # the library, which would segfault
        return np.full(len(q_values), OUT_OF_DOMAIN)

    # nodes of the size distribution integral
    r_end = _integration_range(mu, s)
    radii = 0.5 * r_end * (_NODES + 1.0)
    r_weights = 0.5 * r_end * _WEIGHTS

    sd_param = _make_param([n_mean, s, P_EXPONENT, mu])
    p_of_r = np.array([_sd_lognorm(r, ctypes.byref(sd_param)) for r in radii])
    # weight of each node in the size distribution integral
    node_weights = r_weights * p_of_r

    sq_param = _make_param([R_HS_FACTOR * mu, ETA_HS])
    sq_ref = ctypes.byref(sq_param)

    ff_param = _make_param(
        [
            0.0,  # R_core, set per node below
            dR,
            eta_core,
            ETA_SH,
            x_solv,
            x_solv,
            eta_solv,
        ],
        kernel_selector=KSHLIN1,
    )
    ff_ref = ctypes.byref(ff_param)

    polynom_param = _make_param(polynom_values)
    polynom_ref = ctypes.byref(polynom_param)

    intensity = np.empty(len(q_values))
    amplitude = np.empty(len(radii))
    for i, q in enumerate(q_values):
        # SASfit functions are not vectorized, so loop over the nodes
        for j, r in enumerate(radii):
            ff_param.p[0] = r
            amplitude[j] = _ff_kshlin(q, ff_ref)

        # <F> and <|F|^2> over the size distribution
        mean_f = np.dot(node_weights, amplitude)
        mean_f2 = np.dot(node_weights, amplitude * amplitude)

        # decoupling approach, see SQ_how == 1 in sasfit_old/sasfit.c
        structure = _sq_hard_sphere_gh(q, sq_ref)
        intensity[i] = (
            mean_f2
            + mean_f * mean_f / n_mean * (structure - 1.0)
            + _ff_polynom(q, polynom_ref)
        )

    return intensity
