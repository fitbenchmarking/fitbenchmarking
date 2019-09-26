.. _extending-fitbenchmarking:

Extending Fitbenchmarking
=========================

.. _problem-groups:

Adding additional problem groups
--------------------------------

*This section describes how to add a problem group to the fit benchmarking
software. The default problem groups that come with this software are,
at the moment of writing this, neutron, NIST, CUTEst and Muon.*

1. Add your problem file directory in
   ``fitbenchmarking/benchmark_problems/``. Some examples of how this
   should look like are available in the same dir.

2. Modify ``example_scripts/example_runScripts.py`` to run new problem
   set in ``fitbenchmarking/benchmark_problems/``.


.. _problem-types:

Adding additional fitting problem definition types
--------------------------------------------------

**Fitting problem definition types currently supported**

At the time of writing, the types (formats) that are currently supported
are:

  - Native (Fitbenchmark)
  - NIST

An example of the native and NIST formats can be seen in
``benchmark_problems/Neutron_data/`` and ``benchmark_problems/NIST/``,
respectively.

**Adding new fitting problem definition types**

Follow the following steps

1. Create ``parse_{type}_data.py`` which
   contains a child class of ``BaseFittingProblem`` in
   ``parsing/base_fitting_problem.py`` that processes the type (format) and
   initialise the class with appropriate attributes (examples can be found
   in ``parse_{nist/fitbenchmark}_data.py``)
2. In ``parsing/parse.py``
   alter the function ``determine_problem_type()`` such that it determines
   the new type
3. In ``parsing/parse.py`` add a new if statement to
   ``parse_problem_file()`` to call the user defined
   ``parse_{type}_data.py`` class

.. _fitting_software:

Adding additional fitting software
----------------------------------
*This section describes how to add additional software to benchmark against
the available problems. The steps below should be used as orientation as
there is no straight forward way to adding a software to fitBenchmarking
at the moment.*

1. In the ``fitbenchmarking/fitbenchmarking/`` folder, add an extra
   ``elif`` for your software in the following functions:

   -  fitbenchmarking_one_problem.py -> fit_one_function_def
   -  fitting/plotting/plots.py -> get_start_guess_data
   -  fitting/prerequisites.py -> prepare_software_prerequisites

2. In the folder ``fitbenchmarking/fitbenchmarking/fitting/`` create a
   python script that deals with the specifics of your algorithm. There
   are examples for the scipy and mantid fitting algorithms.

3. For additional support please see :ref:`getting-started`.
