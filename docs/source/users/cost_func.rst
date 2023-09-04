.. _cost_func:

==============
Cost functions
==============

Fitbenchmarking supports multiple cost functions. These can be set via the ``cost_func_type`` option in :ref:`fitting_option`.

Fitbenchmarking is designed to work with problems that have the form

.. math::

   \min_p F(r(x,y,p)).
   
The function :math:`F(\cdot)` is known as the cost function,
while the function :math:`r(x,u,p)` is known as the *residual* of the cost function.
The residual will generally be zero if the fit was perfect.
Both of these quantities together define a cost function in FitBenchmarking.

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

- Weighted non-linear least squares cost function with log-likelihood evaluation

    .. currentmodule:: fitbenchmarking.cost_func.loglike_nlls_cost_func
    .. autoclass:: fitbenchmarking.cost_func.loglike_nlls_cost_func.LoglikeNLLSCostFunc
               :noindex:
