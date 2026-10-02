.. _lsqfit_format:

======
lsqfit
======

The lsqfit format extends the native FitBenchmark format to support problems
that use external Python functions and include covariance matrices.

File Format
===========

lsqfit problems use the FitBenchmark format with the following required fields:

.. code-block:: text

    # Fitbenchmark Problem
    software = 'lsqfit'
    name = 'Problem Name'
    description = 'Problem description'
    input_file = 'data_files/problem.dat'
    function = 'module=path/to/functions,func=function_name,param1=value1,param2=value2'
    plot_scale = 'linear'

Fields
------

**software**: Must be ``'lsqfit'`` to trigger the lsqfit parser.

**function**: Specifies the model function with the format:
``module=<path>,func=<name>,param1=val1,param2=val2,...``

  - ``module``: Path to Python module containing the function (relative to problem file directory).
    Supports nested paths like ``functions/periodic_cosh_function``.
  - ``func``: Name of the function to call in the module.
  - Additional parameters: Starting values for each parameter (these are parsed as floats if possible).

**priors** (optional): Prior specifications for parameters (empty string if not used).
Format: ``param1=mean(sdev),param2=mean(sdev)``

Example: ``priors = 'a=0.1(0.02),E=0.7(0.1)'``

Data Files
==========

**Data file** (``input_file``): Standard FitBenchmark format with header:

.. code-block:: text

    # x y e
    1.0 0.5 0.1
    2.0 0.3 0.1
    3.0 0.1 0.05

Columns: x (independent variable), y (dependent variable), e (error/uncertainty)

**Covariance** (optional): If a file named ``<basename>_cov.txt`` exists, it will be
read as a covariance matrix and stored in ``problem.additional_info['covariance']``.

Model Function
===============

The function specified in the ``function`` field must:

- Accept ``x`` as the first argument (independent variable)
- Accept parameters as keyword arguments matching the names specified in ``function``
- Return a numpy array or scalar

Example:

.. code-block:: python

    import numpy as np

    def periodic_cosh(x, a, E, Nt):
        """Periodic single-cosh model for correlator fits."""
        return a**2 * (np.exp(-E * x) + np.exp(-E * (Nt - x)))

Example Problem
===============

A complete lsqfit problem directory structure:

.. code-block:: text

    problem_name/
    ├── problem.txt                    # Problem definition
    ├── data_files/
    │   ├── problem.dat               # Data file
    │   └── problem_cov.txt           # Covariance matrix (optional)
    └── functions/
        └── model_functions.py        # Python module with functions

Problem definition file (``problem.txt``):

.. code-block:: text

    # Fitbenchmark Problem
    software = 'lsqfit'
    name = 'Example Problem'
    description = 'Example lsqfit problem'
    input_file = 'data_files/problem.dat'
    function = 'module=functions/model_functions,func=periodic_cosh,a=0.1,E=0.7,Nt=48'
    priors = ''
    plot_scale = 'logy'

Usage
=====

Run lsqfit problems like any other FitBenchmarking problem:

.. code-block:: bash

    fitbenchmarking -o options.ini -p path/to/problem_name

The lsqfit parser extends the FitBenchmarkParser to handle function loading and covariance
parsing. All FitBenchmarking minimizers work with lsqfit problems.
