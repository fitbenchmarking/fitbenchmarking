.. _lsqfit_format:

******************
lsqfit File Format
******************

The lsqfit file format is based on :ref:`native`, extended to support
problems that use external Python functions and include covariance matrices.

An example of an lsqfit problem is:

.. literalinclude:: ../../../../examples/benchmark_problems/CCPTEP_lsqfit_samples/ASB1M4_av.txt

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software
  Must be ``'lsqfit'`` to trigger the lsqfit parser.

name, description
  As described in the native format.

input_file
  The name of a file containing the data to fit, as described in the native
  format. The file must be in a subdirectory named ``data_files`` and follow
  the standard ``# x y e`` column convention.

function
  Specifies the model function with the format:
  ``module=<path>,func=<name>,param1=val1,param2=val2,...``

  - *module*: Path to Python module containing the function (relative to the
    problem file directory). Supports nested paths such as
    ``functions/periodic_cosh_function``.
  - *func*: Name of the function to call in the module.
  - Additional parameters: Starting values for each parameter (parsed as
    floats if possible).

  The function specified must accept ``x`` as the first argument (the
  independent variable) and accept parameters as keyword arguments matching
  the names specified in the ``function`` field. For example:

  .. code-block:: python

      import numpy as np

      def periodic_cosh(x, a, E, Nt):
          return a**2 * (np.exp(-E * x) + np.exp(-E * (Nt - x)))

fixed_params
  An optional comma-separated list of parameter names to hold fixed during
  fitting. Each name must appear in the ``function`` field; its value is
  taken from the starting value given there.

  For example, with ``function = '...,Nt=48'``, setting
  ``fixed_params = 'Nt'`` keeps ``Nt`` fixed at ``48`` throughout the fit.

Covariance matrix
=================

If a file named ``<basename>_cov.txt`` exists alongside the data file, it
will be read as a covariance matrix and stored in
``problem.additional_info['covariance']``.

.. note::

   Storing a covariance matrix does not automatically affect the fit. To use
   the full covariance in the objective function you must select the
   ``whitened_nlls`` cost function (see :ref:`fitting_option`). Using any
   other cost function with a covariance matrix present will produce a warning.
