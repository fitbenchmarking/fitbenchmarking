.. _hessian_option:

###############
Hessian Options
###############

The Hessian section allows you to control which methods for computing Hessians the software uses.

.. _analytic-hes:

Analytic (:code:`analytic`)
---------------------------

Analytic Hessians can only be used for specific :ref:`problem_def`. Currently
the supported formats are cutest and NIST. The only option is:

* ``default`` - use the analytic derivative provided by a supported format.

Default is ``default``

.. code-block:: rst

    [HESSIAN]
    analytic: default

.. _scipy-hes:

SciPy (:code:`scipy`)
---------------------

Calculates the Hessian from the Jacobian using the finite differencing in
SciPy, this uses ``scipy.optimize._numdiff.approx_derivative``. The supported
options are:

* ``2-point`` - use the first order accuracy forward or backward difference.
* ``3-point`` - use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* ``cs`` - use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.

Default is ``2-point``

**Licence** SciPy is available under a `3-clause BSD Licence <https://github.com/scipy/scipy/blob/master/LICENSE.txt>`__.  Individual packages may have their own (compatible) licences, as listed `here <https://github.com/scipy/scipy/blob/master/LICENSES_bundled.txt>`__.

.. code-block:: rst

    [HESSIAN]
    scipy: 2-point

.. _defaulthessian:

Default Hessian (:code:`default`)
---------------------------------

Hessian information is not passed to minimizers. The only option is:

* ``default`` - don't pass Hessian information to minimizers.

Default is ``default``

.. code-block:: rst

    [HESSIAN]
    default: default

.. _numdifftools-hes:

Numdifftools (:code:`numdifftools`)
-----------------------------------

Calculates the Hessian from the Jacobian using the python package :code:`numdifftools`.
We allow the user to change the method used, but other options
(e.g, the step size generator and the order of the approximation) are set to the defaults.
The supported options are:

* ``central`` - central differencing.  Almost as accurate as complex, but with no restriction on the type of function.
* ``forward`` - forward differencing.
* ``backward`` - backward differencing.
* ``complex`` - based on the complex-step derivative method of `Lyness and Moler <http://epubs.siam.org/doi/abs/10.1137/0704019>`__.  Usually the most accurate, provided the function is analytic.
* ``multicomplex`` - extends complex method using multicomplex numbers. (see, e.g., `Lantoine, Russell, Dargent (2012) <https://dl.acm.org/doi/10.1145/2168773.2168774>`__).

Default is ``central``.

**Licence** :code:`numdifftools` is available under a `3-clause BSD Licence <https://github.com/pbrod/numdifftools/blob/master/LICENSE.txt>`__.

.. code-block:: rst

    [HESSIAN]
    numdifftools: central

Best Available (:code:`best_available`)
---------------------------------------

A flexible option which uses :ref:`analytic-hes` where available and
:ref:`scipy-jac` with ``method=2-point`` when the analytic would fail.
This may be useful when testing large problem sets with multiple sources.

 The only option is:

* ``default`` - use analytic hessian if available, otherwise use scipy 2-point.

Default is ``default``

.. code-block:: rst

    [HESSIAN]
    best_available: default
