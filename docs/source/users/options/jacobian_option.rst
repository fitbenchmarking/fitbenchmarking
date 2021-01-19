.. _jacobian_option:

################
Jacobian Options
################

The Jacobian section allows you to control which methods for computing Jacobians the software uses.  

Analytic (:code:`analytic`)
---------------------------

Analytic Jacobians can only be used for specific :ref:`problem_def`. Currently
the supported formats are:

* ``cutest``
* ``NIST``
  
Default is ``cutest``

.. code-block:: rst

    [JACOBIAN]
    analytic: cutest

.. _scipy-jac:

SciPy (:code:`scipy`)
---------------------

Calculates the Jacobian using the numerical Jacobian in
SciPy, this uses ``scipy.optimize._numdiff.approx_derivative``. The supported
options are:

* ``2-point`` - use the first order accuracy forward or backward difference.
* ``3-point`` - use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* ``cs`` - use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.

Default is ``2-point``

.. code-block:: rst

    [JACOBIAN]
    scipy: 2-point

.. _numdifftools-jac:

Numdifftools (:code:`numdifftools`)
-----------------------------------

Calculates the Jacobian using the python package :code:`numdifftools`.
We allow the user to change the method used, but other options
(e.g, the step size generator and the order of the approximaton) are set the defaults.
The supported options are:

* ``central`` - central differencing.  Almost as accurate as complex, but with no restriction on the type of function.
* ``forward`` - forward differencing.
* ``backward`` - backward differencing.
* ``complex`` - based on the complex-step derivative method of `Lyness and Moler <http://epubs.siam.org/doi/abs/10.1137/0704019>`_.  Usually the most accurate, provided the function is analytic.  
* ``multicomplex`` - extends complex method using multicomplex numbers. (see, e.g., `Lantoine, Russell, Dargent (2012) <https://dl.acm.org/doi/10.1145/2168773.2168774>`_).

Default is ``central``.

.. code-block:: rst

    [JACOBIAN]
    numdifftools: central
