.. _extending-fitbenchmarking:

Extending Fitbenchmarking
=========================

.. _problem-groups:

Adding additional problem groups
--------------------------------

*This section describes how to add a problem group to the fit benchmarking
software. The default problem groups that come with this software are,
at the moment of writing this, CUTEst, Muon, Neutron, NIST, SAS_modelling,
and simple_tests.*

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
  - Sasview

An example of these formats can be seen in
``benchmark_problems/Neutron_data/``,
``benchmark_problems/NIST/``,
and ``benchmark_problems/SAS_modelling/``
respectively.

**Adding new fitting problem definition types**

Follow the following steps

1. Create ``parse_{type}_data.py`` which
   contains a child class of ``BaseFittingProblem`` in
   ``parsing/base_fitting_problem.py`` that processes the type (format) and
   initialise the class with appropriate attributes (examples can be found
   in ``parse_{nist/fitbenchmark/sasview}_data.py``).
   As a minimum this must implement the abstract get_function method which
   returns a list of callable-initial parameter pairs.
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
the available problems.*

In FitBenchmarking, controllers are used to interface into the various fitting
softwares. Controllers are responsible for converting the problem into a format
that the fitting software can use, and converting the result back to a
standardised format (numpy arrays). As well as this, the controller must be
written so that the fitting is separated from the preparation wherever possible
in order to give accurate timings for the fitting. Examples of these
controllers can be found in ``fitbenchmarking/fitting/controllers``.

In order to add a new controller, you will need to:

1. Create a new subclass of BaseSoftwareController in
   ``fitbenchmarking/fitting/controllers``.
   This should implement 4 functions:

   -  ``__init__()``: Initialise anything that is needed specifically for the
      software, do any work that can be done without knowledge of the
      minimizer to use, or function to fit, and call ``super().__init__()``.
   -  ``setup()``: Do any work that must be done only after knowing the
      minimizer to use and the function to fit. E.g. creating function wrappers
      around a callable.
   -  ``fit()``: Run the fitting. This will be timed so should include only
      what is needed to fit the data.
   -  ``cleanup()``: Convert the results into the expected numpy arrays and
      store them in the results variables
      (``self.results``, ``self.final_params``, ``self.success``)

2. Import your controller and add it to the dictionary 'controllers' in
   ``fitbenchmarking/fitbenchmark_one_problem.py``

3. Document the available minimizers (currently done by adding to
   ``fitbenchmarking/fitbenchmarking_default_options.json``)

4. Create tests for the software in
   ``fitbenchmarking/fitting/tests/test_controllers.py``.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.
