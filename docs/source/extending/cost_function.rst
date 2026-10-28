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
   Then implement the methods:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.eval_cost()
              :noindex:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.jac_res()
              :noindex:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.jac_cost()
              :noindex:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.hes_res()
              :noindex:

    -  .. automethod:: fitbenchmarking.cost_func.base_cost_func.CostFunc.hes_cost()
              :noindex:

  .. note::
     Non-linear least squares cost functions should subclass
     :class:`~fitbenchmarking.cost_func.nlls_base_cost_func.BaseNLLSCostFunc`
     instead, and implement the residuals for a single dataset:

      -  .. automethod:: fitbenchmarking.cost_func.nlls_base_cost_func.BaseNLLSCostFunc.eval_r_single_dataset()
                :noindex:

     The residuals for the whole problem are then evaluated by

      -  .. automethod:: fitbenchmarking.cost_func.nlls_base_cost_func.BaseNLLSCostFunc.eval_r()
                :noindex:

     which is implemented in the base class, and which takes care of calling
     ``eval_r_single_dataset``. This is needed to ensure the multifit capability.

2. Document the available cost functions by:

  * adding ``<cost_func>`` to the ``cost_func_type`` option in :ref:`fitting_option`.
  * updating any example files in the ``examples`` directory
  * adding the new cost function to the :ref:`cost_func` user docs.

3. Create tests for the cost function in
   ``fitbenchmarking/cost_func/tests/test_cost_func.py``.

The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new cost functions, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`
class.

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, data_x, data_y, data_e
          :noindex:

You will also find it useful to implement the subclass members of
:class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc`,
:class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` and
:class:`~fitbenchmarking.hessian.base_hessian.Hessian`.

.. currentmodule:: fitbenchmarking.cost_func.base_cost_func
.. autoclass:: fitbenchmarking.cost_func.base_cost_func.CostFunc
          :members: eval_cost, jac_res, jac_cost, hes_res, hes_cost
          :noindex:

.. currentmodule:: fitbenchmarking.jacobian.base_jacobian
.. autoclass:: fitbenchmarking.jacobian.base_jacobian.Jacobian
          :members: eval
          :noindex:

.. currentmodule:: fitbenchmarking.hessian.base_hessian
.. autoclass:: fitbenchmarking.hessian.base_hessian.Hessian
          :members: eval
          :noindex:
