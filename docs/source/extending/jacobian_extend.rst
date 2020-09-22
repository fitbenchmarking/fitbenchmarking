.. _jacobian_extend:

####################
Adding new Jacobians
####################

*This section describes how to add further methods to approximate the Jacobian within FitBenchmarking*

In order to add a new Jacobian evaluation method,``<jac_method>``,
you will need to:

1. Give the Jacobian method in the :ref:`fitting_option` using the following
   convention ``<jac_method>`` and :ref:`jacobian_option` is added using
   ``<jac_method>`` as the key and the list as possible numerical methods.

2. Create ``fitbenchmarking/jacobian/<jac_method>_jacobian.py``
   which contains a new subclass of ``Jacobian``
   (from ``base_jacobian.py``). Then implement the method ``eval()``, which
   evaluates the Jacobian. The numerical method is set sequentially
   within ``fitbenchmarking.core.fitting_benchmark.loop_over_jacobians`` by
   using the ``method`` attribute of the class.


3. Document the available Jacobians by:

  * updating the docs for :ref:`jacobian_option` in ``docs/source/users/jacobian.rst``
  * updating options via :ref:`options` and :ref:`options_extend`
  * updating any example files in the ``examples`` directory

4. Create tests for the Jacobian evaluation in
   ``fitbenchmarking/jacobian/tests/test_jacobians.py``.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new Jacobian, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
classes:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: cache_fx, cache_rx, cache_r_norm_x
	  :noindex:

.. note::
   If using cached values, use the base class ``cached_func_values`` method that checks
   that the parameters the function is evaluated at and will either use the cached
   result or evaluates the function.
