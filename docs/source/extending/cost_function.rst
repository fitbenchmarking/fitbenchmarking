.. _cost_function:

#########################
Adding new cost functions
#########################

*This section describes how to add cost functions to benchmarking in FitBenchmarking*

In order to add a new cost function, ``<cost_func>``,
you will need to:

1. Create ``fitbenchmarking/cost_func/<cost_func>_cost_func.py``,
   which contains a new subclass of
   :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`.
   Then implement the method:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.eval_cost()
              :noindex:

2. Document the available cost functions by:

  * adding ``<cost_func>`` to the ``cost_func_type`` option in :ref:`fitting_option`.
  * updating any example files in the ``examples`` directory

3. Create tests for the cost function in
   ``fitbenchmarking/cost_func/tests/test_cost_func.py``.



The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new cost functions, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
and subclasses of :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc` class:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, cache_model_x, data_x, data_y, data_e
          :noindex:

.. currentmodule:: fitbenchmarking.cost_func.base_cost_func
.. autoclass:: fitbenchmarking.cost_func.base_cost_func.CostFunc
          :members: cache_cost_x
          :noindex:
