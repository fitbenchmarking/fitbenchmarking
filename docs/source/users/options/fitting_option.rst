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

* ``analytic`` - uses the analytic Jacobian extracted from the fitting problem.
* ``scipy`` -  uses :ref:`SciPy's finite difference Jacobian approximations <scipy-jac>`
* ``numdifftools`` - uses the python package :ref:`numdifftools <numdifftools-jac>`.
  
Default is ``scipy``

.. code-block:: rst

    [FITTING]
    jac_method: scipy

.. warning::

   Currently analytic Jacobians are available are only available for
   problems that use the cutest and NIST parsers.

Cost function (:code:`cost_func_type`)
--------------------------------------

This sets the cost function to be used for the given data. Current cost
functions supported are:

* ``nlls`` - This sets the cost function to be non-weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.nlls_cost_func.NLLSCostFunc`.

* ``weighted_nlls`` - This sets the cost function to be weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.weighted_nlls_cost_func.WeightedNLLSCostFunc`.

* ``hellinger_nlls`` - This sets the cost function to be the Hellinger cost function, :class:`~fitbenchmarking.cost_func.root_nlls_cost_func.HellingerNLLSCostFunc`.


Default is ``nlls``

.. code-block:: rst

    [FITTING]
    cost_func_type: weighted_nlls
