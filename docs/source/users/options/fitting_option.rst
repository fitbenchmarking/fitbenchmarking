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
* ``gradient_free`` (default software)
* ``gsl`` (external software -- see :ref:`external-instructions`)
* ``levmar`` (external software -- see :ref:`extra_dependencies`)
* ``mantid`` (external software -- see :ref:`external-instructions`)
* ``matlab`` (external software -- see :ref:`external-instructions`)
* ``matlab_curve`` (external software -- see :ref:`external-instructions`)
* ``matlab_opt`` (external software -- see :ref:`external-instructions`)
* ``matlab_stats`` (external software -- see :ref:`external-instructions`)
* ``minuit`` (default software)
* ``ralfit`` (external software -- see :ref:`external-instructions`)
* ``scipy`` (default software)
* ``scipy_ls`` (default software)
* ``scipy_go`` (default software)


Default are ``bumps``, ``dfo``, ``gradient_free``, ``minuit``, ``scipy``, ``scipy_ls`` and ``scipy_go``

.. code-block:: rst

    [FITTING]
    software: bumps
              dfo
              minuit
              scipy
              scipy_ls
              scipy_go

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

.. _algorithm_type:

Algorithm type (:code:`algorithm_type`)
---------------------------------------

This is used to select what type of algorithm is used within a specific software.
For a full list of available minimizers for each algorithm type, see :ref:`minimizer_types`. 
The options are:

* ``all`` - all minimizers
* ``ls`` - least-squares fitting algorithms
* ``deriv_free`` - derivative free algorithms (these are algorithms that cannot use
  information about derivatives -- e.g., the ``Simplex`` method in ``Mantid``),
  see :ref:`deriv_free`.
* ``general`` - minimizers which solve a generic `min f(x)`
* ``simplex`` - derivative free simplex based algorithms e.g. Nelder-Mead, see :ref:`Simplex <simplex>`
* ``trust_region`` - algorithms which employ a trust region approach,  see :ref:`trust_region`
* ``levenberg-marquardt`` - minimizers that use the Levenberg Marquardt algorithm, see :ref:`Levenberg-Marquardt <levenberg_marquardt>`.
* ``gauss_newton`` - minimizers that use the Gauss Newton algorithm, see :ref:`Gauss-Newton <gauss_newton>`
* ``bfgs`` - minimizers that use the BFGS algorithm, see :ref:`BFGS <bfgs>`
* ``conjugate_gradient`` - Conjugate Gradient algorithms, see :ref:`Conjugate Gradient <conjugate_gradient>`
* ``steepest_descent`` - Steepest Descent algorithms, see :ref:`Steepest Descent <steepest_descent>`
* ``global_optimization`` - Global Optimization algorithms

Default is ``all``

.. code-block:: rst

    [FITTING]
    algorithm_type: all

.. warning::

   Choosing an option other than ``all`` may deselect certain
   minimizers set in the options file


Jacobian method (:code:`jac_method`)
------------------------------------

This sets the Jacobian used. Current Jacobian methods are:

* ``analytic`` - uses the analytic Jacobian extracted from the fitting problem.
* ``scipy`` -  uses :ref:`SciPy's finite difference Jacobian approximations <scipy-jac>`.
* ``default`` - uses the default derivative approximation implemented in the minimizer.
* ``numdifftools`` - uses the python package :ref:`numdifftools <numdifftools-jac>`.
  
Default is ``default``

.. code-block:: rst

    [FITTING]
    jac_method: scipy

.. warning::

   Currently analytic Jacobians are available are only available for
   problems that use the cutest and NIST parsers.


Hessian method (:code:`hes_method`)
------------------------------------

This sets the Hessian used. Current Hessian methods are:

* ``default`` - Hessian information is not passed to minimizers
* ``analytic`` - uses the analytic Hessian extracted from the fitting problem.
  
Default is ``default``

.. code-block:: rst

    [FITTING]
    hes_method: default

.. warning::

   Currently analytic Hessians are available are only available for
   problems that use the NIST parser and for the ``nlls`` and
   ``weighted_nlls`` cost functions.

Cost function (:code:`cost_func_type`)
--------------------------------------

This sets the cost function to be used for the given data. Current cost
functions supported are:

* ``nlls`` - This sets the cost function to be non-weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.nlls_cost_func.NLLSCostFunc`.

* ``weighted_nlls`` - This sets the cost function to be weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.weighted_nlls_cost_func.WeightedNLLSCostFunc`.

* ``hellinger_nlls`` - This sets the cost function to be the Hellinger cost function, :class:`~fitbenchmarking.cost_func.hellinger_nlls_cost_func.HellingerNLLSCostFunc`.

* ``poisson`` - This sets the cost function to be the Poisson Deviation cost function, :class:`~fitbenchmarking.cost_func.poisson_cost_func.PoissonCostFunc`.


Default is ``weighted_nlls``

.. code-block:: rst

    [FITTING]
    cost_func_type: weighted_nlls
