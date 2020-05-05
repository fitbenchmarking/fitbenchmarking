.. _jacobian:

################
Jacobian options
################

Currently FitBenchmarking uses SciPy's `numerical finite difference <https://github.com/scipy/scipy/blob/912c54cd6473225c902377df410258839511b863/scipy/optimize/_numdiff.py#L198>`_ approximation to the Jacobian. The finite difference schemes implemented are:

* `2-point`: use the first order accuracy forward or backward difference.
* `3-point`: use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* `cs`: use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.

The options can be set via the :ref:`options`.
