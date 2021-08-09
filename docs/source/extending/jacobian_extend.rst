.. _jacobian_extend:

####################
Adding new Jacobians
####################

*This section describes how to add further methods to approximate the
Jacobian within FitBenchmarking*

In order to add a new Jacobian evaluation method, ``<jac_method>``,
you will need to:

1. Create ``fitbenchmarking/jacobian/<jac_method>_jacobian.py``,
   which contains a new subclass of
   :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian`.
   Then implement the methods:

    -  .. automethod:: fitbenchmarking.jacobian.base_jacobian.Jacobian.eval()
              :noindex:
    -  .. automethod:: fitbenchmarking.jacobian.base_jacobian.Jacobian.eval_cost()
              :noindex:

   The numerical method is set sequentially within
   :meth:`~fitbenchmarking.core.fitting_benchmarking.loop_over_jacobians()` by
   using the ``method`` attribute of the class.

2. Enable the new method as an option in :ref:`fitting_option`,
   following the instructions in :ref:`options_extend`.  Specifically:
   
   * Amend the ``VALID_FITTING`` dictionary so that the element associated
     with the ``jac_method`` key contains the new ``<jac_method>``.
     
   * Extend the ``VALID_JACOBIAN`` dictionary to have a new
     key ``<jac_method>``, with the associated element being a list of
     valid options for this Jacobian.
     
   * Extend the ``DEFAULT_JACOBIAN`` dictionary to have a new key
     ``<jac_method>``, with the associated element being a subset of the
     valid options added in ``VALID_JACOBIAN`` in the previous step.

   * Amend the file ``fitbenchmarking/utils/tests/test_options_jacobian.py`` to
     include tests for the new options.

3. Document the available Jacobians by:

  * adding a list of available ``method`` options to the docs for :ref:`jacobian_option`,
    and including licencing information, if appropriate.
  * updating any example files in the ``examples`` directory

4. Create tests for the Jacobian evaluation in
   ``fitbenchmarking/jacobian/tests/test_jacobians.py``.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new Jacobian, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
and subclasses of :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, cache_model_x, data_x, data_y, data_e
          :noindex:

.. currentmodule:: fitbenchmarking.cost_func.base_cost_func
.. autoclass:: fitbenchmarking.cost_func.base_cost_func.CostFunc
          :members: eval_cost, cache_cost_x
          :noindex:


.. note::
   If using cached values, use the
   :meth:`~fitbenchmarking.jacobian.base_jacobian.Jacobian.cached_func_values` method,
   which first checks if a cached function evaluation is available to use
   for the given parameters.
