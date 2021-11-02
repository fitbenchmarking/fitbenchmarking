.. _hessian_extend:

###################
Adding new Hessians
###################

*This section describes how to add further methods to approximate the
Hessian within FitBenchmarking*

In order to add a new Hessian evaluation method, ``<hes_method>``,
you will need to:

1. Create ``fitbenchmarking/hessian/<hes_method>_hessian.py``,
   which contains a new subclass of
   :class:`~fitbenchmarking.hessian.base_hessian.hessian`.
   Then implement the method:

    -  .. automethod:: fitbenchmarking.hessian.base_hessian.Hessian.eval()
              :noindex:

   The method is set sequentially within
   :meth:`~fitbenchmarking.core.fitting_benchmarking.loop_over_hessians()` by
   using the ``method`` attribute of the class.

2. Enable the new method as an option in :ref:`fitting_option`,
   following the instructions in :ref:`options_extend`.  Specifically:
   
   * Amend the ``VALID_FITTING`` dictionary so that the element associated
     with the ``hes_method`` key contains the new ``<hes_method>``.

3. Document the available Hessians by:

  * adding to the list of available ``method`` options under ``hes_method`` in :ref:`fitting_option`.
  * updating any example files in the ``examples`` directory

4. Create tests for the Hessian evaluation in
   ``fitbenchmarking/hessian/tests/test_hessians.py``.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new Hessian, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
and subclasses of :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian`:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, data_x, data_y, data_e
          :noindex:

.. currentmodule:: fitbenchmarking.jacobian.base_jacobian
.. autoclass:: fitbenchmarking.jacobian.base_jacobian.Jacobian
          :members: eval
          :noindex:
