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
* ``ceres`` (external software -- see :ref:`external-instructions`)
* ``CUTEst`` (external software -- see :ref:`external-instructions`)
* ``dfo`` (external software -- see :ref:`extra_dependencies`)
* ``galahad`` (external software -- see :ref:`external-instructions`)
* ``gofit`` (external software -- see :ref:`extra_dependencies`)
* ``gradient_free`` (external software -- see :ref:`extra_dependencies`)
* ``gsl`` (external software -- see :ref:`external-instructions`)
* ``horace`` (external software -- see :ref:`external-instructions`)
* ``levmar`` (external software -- see :ref:`extra_dependencies`)
* ``lmfit`` (external software -- see :ref:`extra_dependencies`)
* ``mantid`` (external software -- see :ref:`external-instructions`)
* ``matlab`` (external software -- see :ref:`external-instructions`)
* ``matlab_curve`` (external software -- see :ref:`external-instructions`)
* ``matlab_opt`` (external software -- see :ref:`external-instructions`)
* ``matlab_stats`` (external software -- see :ref:`external-instructions`)
* ``minuit`` (external software -- see :ref:`extra_dependencies`)
* ``nlopt`` (external software -- see :ref:`extra_dependencies`)
* ``paramonte`` (external software -- see :ref:`extra_dependencies`)
* ``ralfit`` (external software -- see :ref:`external-instructions`)
* ``scipy`` (default software)
* ``scipy_ls`` (default software)
* ``scipy_leastsq`` (default software)
* ``scipy_go``
* ``theseus`` (external software -- see :ref:`external-instructions`)


Default software options are ``scipy`` and ``scipy_ls``

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
* ``MCMC`` - Markov Chain Monte Carlo algorithms

Default is ``all``

.. code-block:: rst

    [FITTING]
    algorithm_type: all

.. warning::

   Choosing an option other than ``all`` may deselect certain
   minimizers set in the options file


Jacobian method (:code:`jac_method`)
------------------------------------

This sets the Jacobian used.
Choosing multiple options via a new line seperated list will result in all
combinations being benchmarked.
Current Jacobian methods are:

* ``analytic`` - uses the analytic Jacobian extracted from the fitting problem.
* ``scipy`` -  uses :ref:`SciPy's finite difference Jacobian approximations <scipy-jac>`.
* ``default`` - uses the default derivative approximation implemented in the minimizer.
* ``numdifftools`` - uses the python package :ref:`numdifftools <numdifftools-jac>`.
* ``best_available`` - uses the analytic jacobian if it is available, otherwise uses a Scipy jacobian.

Default is ``best_available``

.. code-block:: rst

    [FITTING]
    jac_method: best_available

.. warning::

   Currently analytic Jacobians are only available for
   problems that use the cutest and NIST parsers.


Hessian method (:code:`hes_method`)
------------------------------------

This sets the Hessian used.
Choosing multiple options via a new line seperated list will result in all
combinations being benchmarked.
Current Hessian methods are:

* ``default`` - Hessian information is not passed to minimizers
* ``analytic`` - uses the analytic Hessian extracted from the fitting problem.
* ``scipy`` -  uses :ref:`SciPy's finite difference approximations <scipy-hes>`.
* ``numdifftools`` - uses the python package :ref:`numdifftools <numdifftools-hes>`.
* ``best_available`` - uses the analytic hessian if it is available, otherwise uses a Scipy hessian.

Default is ``best_available``

.. code-block:: rst

    [FITTING]
    hes_method: best_available

.. warning::

   Currently analytic Hessians are only available for
   problems that use the cutest and NIST parsers.

Cost function (:code:`cost_func_type`)
--------------------------------------

This sets the cost functions to be used for the given data.
Choosing multiple options via a new line seperated list will result in all
combinations being benchmarked.
Currently supported cost functions are:

* ``nlls`` - This sets the cost function to be non-weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.nlls_cost_func.NLLSCostFunc`.

* ``weighted_nlls`` - This sets the cost function to be weighted non-linear least squares, :class:`~fitbenchmarking.cost_func.weighted_nlls_cost_func.WeightedNLLSCostFunc`.

* ``hellinger_nlls`` - This sets the cost function to be the Hellinger cost function, :class:`~fitbenchmarking.cost_func.hellinger_nlls_cost_func.HellingerNLLSCostFunc`.

* ``poisson`` - This sets the cost function to be the Poisson Deviation cost function, :class:`~fitbenchmarking.cost_func.poisson_cost_func.PoissonCostFunc`.


Default is ``weighted_nlls``

.. code-block:: rst

    [FITTING]
    cost_func_type: weighted_nlls

Maximum Runtime (:code:`max_runtime`)
--------------------------------------

This sets the maximum runtime a minimizer has to solve one benchmark
problem `num_runs` number of times, where `num_runs` is another option a
user can set. If the minimizer is still running after the maximum time
has elapsed, then this result will be skipped and FitBenchmarking will move
on to the next minimizer / benchmark dataset combination. The main purpose
of this option is to get to result tables quicker by limit the runtime.

`max_runtime` is set by specifying a number in unit of seconds. Please note
that depending on platform the time specified with `max_runtime` may not
match entirely with the absolute run-times specified in tables. Hence you
may have to experiment a bit with this option to get the cutoff you want.

Default is 600 seconds

.. code-block:: rst

    [FITTING]
    max_runtime: 600
