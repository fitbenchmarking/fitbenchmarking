.. _fitting_option:

###############
Fitting Options
###############

Options that control the benchmarking process are set here.


Software (:code:`software`)
---------------------------

Software is used to select the fitting software to benchmark, this should be
a newline-separated list. Available options are:

* ``bumps`` (default software)
* ``dfo`` (default software)
* ``gsl`` (external software -- see :ref:`external-instructions`)
* ``mantid`` (external software -- see :ref:`external-instructions`)
* ``minuit`` (default software)
* ``ralfit`` (external software -- see :ref:`external-instructions`)
* ``scipy`` (default software)
* ``scipy_ls`` (default software)


Default are ``bumps``, ``dfo``, ``minuit``, ``scipy``, and ``scipy_ls``

.. code-block:: rst

    [FITTING]
    software: bumps
              dfo
              minuit
              scipy
              scipy_ls

.. warning::

   Software must be listed to be here to be run.
   Any minimizers set in :ref:`minimizer_option` will not be run if the software is not also
   present in this list.


Number of minimizer runs (:code:`num_runs`)
-------------------------------------------

Sets the number of runs to average each fit over.

Default is ``5``

.. code-block:: rst

    [FITTING]
    num_runs: 5

Algorithm type (:code:`algorithm_type`)
---------------------------------------

This is used to select what type of algorithm is used within a specific software.
The options are:

* ``all`` - all minimizers
* ``ls`` - least-squares fitting algorithms
* ``deriv_free`` - derivative free algorithms (these are algorithms that do not require an information about derivatives. For example, the ``Simplex`` method in ``Mantid`` does not require derivative information but ``lm-scipy-no-jac`` in ``scipy_ls`` does but the derivative is handle internally within the software package)
* ``general`` - minimizers which solve a generic `min f(x)`

Default is ``all``

.. code-block:: rst

    [FITTING]
    algorithm_type: all

.. warning::

   Choosing an option other than ``all`` may deselect certain
   minimizers set in the options file



Use errors (:code:`use_errors`)
-------------------------------


This will switch between weighted and unweighted least squares.
If ``use_errors=True``, and no errors are supplied, then
``e[i]`` will be set to ``sqrt(abs(y[i]))``.
Errors below ``1.0e-8`` will be clipped to that value.

Default is ``True`` (``yes``/``no`` can also be used)

.. code-block:: rst

    [FITTING]
    use_errors: yes


Jacobian method (:code:`jac_method`)
------------------------------------

This sets the Jacobian used. Current Jacobian methods are:

* ``SciPyFD`` - denotes the use of SciPy's finite difference Jacobian approximations

Default is ``SciPyFD``

.. code-block:: rst

    [FITTING]
    jac_method: SciPyFD


Numerical method (:code:`num_method`)
-------------------------------------

Sets the numerical method used in conjunction with the Jacobian method.
Currently scipy.optimize._numdiff.approx_derivative are the only
methods implemented to calculate finite difference Jacobians.
Scipy options are given as below:

* ``2point`` - use the first order accuracy forward or backward difference.
* ``3point`` - use central difference in interior points and the second order accuracy forward or backward difference near the boundary.
* ``cs`` - use a complex-step finite difference scheme. This assumes that the user function is real-valued and can be analytically continued to the complex plane. Otherwise, produces bogus results.

Default is ``2point``

.. code-block:: rst

    [FITTING]
    num_method: 2point
