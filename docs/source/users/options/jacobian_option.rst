.. _jacobian_option:

################
Jacobian Options
################

The Jacobian section allows you to control which methods for computing Jacobians the software uses.

.. _analytic-jac:

Analytic (:code:`analytic`)
---------------------------

Functions for analytic Jacobians are available for specific :ref:`problem_def`. Specifically, dense jacobian functions are
available for cutest, NIST and Mantid, while sparse jacobians are available for cutest only.
If an analytic jacobian is not available, the benchmark will be skipped. The user can specify custom
jacobian functions for any :ref:`problem_def` except from NIST and cutest, through a problem definition file. 
They can specify a dense and a sparse jacobian, and select which one to use by the following options:

* ``default`` - use the analytic (dense) derivative provided by a supported format or the dense jacobian function provided by the user.
* ``sparse`` - use a sparse jacobian function, either available or provided by the user, to compute the derivative.

Default is ``default``. When dealing with problems of supported formats, if a jacobian function is specified, this will
have priority over the analytic derivative provided by the format.

.. code-block:: rst

    [JACOBIAN]
    analytic: default

.. warning::

    Mantid may return an approximate jacobian, however we are unable to determine when this is the case.

.. _scipy-jac:

SciPy (:code:`scipy`)
---------------------

Calculates the Jacobian using the numerical Jacobian in
SciPy, this uses ``scipy.optimize._numdiff.approx_derivative``. The supported
options are:

* ``2-point`` - use the first order accuracy forward or backward difference.
* ``3-point`` - use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* ``cs`` - use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.
* ``2-point_sparse`` - use 2-point, with a sparsity pattern.

Default is ``2-point``

**Licence** SciPy is available under a `3-clause BSD Licence <https://github.com/scipy/scipy/blob/master/LICENSE.txt>`__.  Individual packages may have their own (compatible) licences, as listed `here <https://github.com/scipy/scipy/blob/master/LICENSES_bundled.txt>`__.

.. code-block:: rst

    [JACOBIAN]
    scipy: 2-point

.. _defaultjacobian:

Solver Default Jacobian (:code:`default`)
--------------------------------------------

This uses the approximation of the Jacobian that is used by default in the minimizer,
and will vary between solvers.  If the minimizer requires the user to pass a Jacobian,
a warning will be printed to the screen and the :ref:`scipy-jac` 2-point
approximation will be used.  The only option is:

* ``default`` - use the default derivative approximation provided by the software.

Default is ``default``

.. code-block:: rst

    [JACOBIAN]
    default: default

.. _numdifftools-jac:

Numdifftools (:code:`numdifftools`)
-----------------------------------

Calculates the Jacobian using the python package :code:`numdifftools`.
We allow the user to change the method used, but other options
(e.g, the step size generator and the order of the approximation) are set the defaults.
The supported options are:

* ``central`` - central differencing.  Almost as accurate as complex, but with no restriction on the type of function.
* ``forward`` - forward differencing.
* ``backward`` - backward differencing.
* ``complex`` - based on the complex-step derivative method of `Lyness and Moler <http://epubs.siam.org/doi/abs/10.1137/0704019>`__.  Usually the most accurate, provided the function is analytic.
* ``multicomplex`` - extends complex method using multicomplex numbers. (see, e.g., `Lantoine, Russell, Dargent (2012) <https://dl.acm.org/doi/10.1145/2168773.2168774>`__).

Default is ``central``.

**Licence** :code:`numdifftools` is available under a `3-clause BSD Licence <https://github.com/pbrod/numdifftools/blob/master/LICENSE.txt>`__.

.. code-block:: rst

    [JACOBIAN]
    numdifftools: central

Best Available (:code:`best_available`)
---------------------------------------

A flexible option which uses :ref:`analytic-jac` where available and
:ref:`scipy-jac` with ``method=2-point`` when the analytic would fail.
This may be useful when testing large problem sets with multiple sources.

 The only option is:

* ``default`` - use analytic jacobian if available, otherwise use scipy 2-point.

Default is ``default``

.. code-block:: rst

    [JACOBIAN]
    best_available: default
