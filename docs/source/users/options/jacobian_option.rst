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
