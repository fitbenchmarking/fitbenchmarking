.. _BenchmarkProblems:

##################
Benchmark problems
##################

To help choose between the different minimizers, FitBenchmarking
comes with some curated Benchmark problems—although it’s straightforward
add custom data sets to the benchmark, if that is more appropriate; see
:ref:`problem_def` for specifics of how to add additional problems in a
supported file format.

We supply some standard nonlinear least-squares test problems in the
form of the `NIST nonlinear regression set <https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`_
and the relevant problems from the `CUTEst problem set <https://github.com/ralna/CUTEst/wiki>`_,
together with some real-world 
data sets that have been extracted from `Mantid <https://www.mantidproject.org>`_ and
`SASView <https://www.sasview.org>`_ usage examples and system tests.
We've made it possible to extend this list by following the steps in 
:ref:`controllers`.

Each of the test problems contain:

* a data set consisting of points :math:`(x_i, y_i)` (with optional errors on :math:`y_i`, :math:`\sigma_i`)
* a definition of the fitting function, :math:`f({\boldsymbol{\beta}};x)`
* (at least) one set of initial values for the function parameters :math:`{\boldsymbol{\beta}}_0`, and
* an optional set of target values that the parameters are expected to reach, :math:`{\boldsymbol{\beta}}_*`.

If a problem doesn’t have observational
errors (e.g., the NIST problem set), then FitBenchmarking can
approximate errors by taking :math:`\sigma_i = \sqrt{y_i}`.
Alternatively, there is an option to disregard errors and solve the
unweighted nonlinear least-squares problem, setting
:math:`\sigma_i = 1.0` irrespective of what has been passed in with the
problem data.

As we work with scientists in other areas, we will extend the problem
suite to encompass new categories. The FitBenchmarking framework has
been designed to make it easy to integrate new problem sets, and a any
new problem set added to the framework can be tested with any and all of
the available fitting methods.
