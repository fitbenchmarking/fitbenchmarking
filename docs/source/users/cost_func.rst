.. _cost_func:

##############
Cost functions
##############

Fitbenchmarking supports multiple different nonlinear least squares cost functions. These can be set via the ``cost_func_type`` option in :ref:`fitting_option`.

The cost functions that are currently supported are:

- Non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.nlls_cost_func.NLLSCostFunc
               :noindex:
- Weighted non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.weighted_nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.weighted_nlls_cost_func.WeightedNLLSCostFunc
               :noindex:
- Root non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.root_nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.root_nlls_cost_func.RootNLLSCostFunc
               :noindex:
