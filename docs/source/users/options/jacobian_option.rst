.. _jacobian_goption:

#################################
Jacobian Numerical Method Options
#################################

The Jacobian section to control the comparison between different methods

Analytic (:code:`analytic`)
---------------------------

Analytic Jacobians can only be used for specific :ref:`problem_def`. Currently
the supported formats are:


* ``cutest``

Default is ``cutest``

.. code-block:: rst

    [JACOBIAN]
    analytic: cutest

SciPy (:code:`scipy`)
---------------------

Sets the numerical Jacobian to be calculated using the numerical Jacobian in
SciPy, this uses scipy.optimize._numdiff.approx_derivative. The supported
options are:

* ``2point`` - use the first order accuracy forward or backward difference.
* ``3point`` - use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* ``cs`` - use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.

Default is ``2point``

.. code-block:: rst

    [JACOBIAN]
    scipy: 2point
