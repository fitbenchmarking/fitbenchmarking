.. _cost_func:

##############
Cost functions
##############

Fitbenchmarking supports multiple different cost functions. These can be set via the ``cost_func_type`` option in :ref:`fitting_option`.

The cost functions that are currently supported are:

- Non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.nlls_cost_func.NLLSCostFunc
               :noindex:
- Weighted non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.weighted_nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.weighted_nlls_cost_func.WeightedNLLSCostFunc
               :noindex:
- Hellinger non-linear least squares cost function

    .. currentmodule:: fitbenchmarking.cost_func.hellinger_nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.hellinger_nlls_cost_func.HellingerNLLSCostFunc
               :noindex:

- Poisson deviance cost function

    .. currentmodule:: fitbenchmarking.cost_func.poisson_cost_func
    .. autoclass:: fitbenchmarking.cost_func.poisson_cost_func.PoissonCostFunc
               :noindex:
