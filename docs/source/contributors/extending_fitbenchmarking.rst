.. _extending-fitbenchmarking:

Extending Fitbenchmarking
=========================

.. _problem-groups:

Adding additional problem groups
--------------------------------

*This section describes how to add a problem group to the fit benchmarking
software. The default problem groups that come with this software are,
CUTEst, Muon, Neutron, NIST, SAS_modelling, and simple_tests.*

1. Add your problem file directory in
   ``fitbenchmarking/benchmark_problems/``. Some examples of how this
   should look like are available in the same dir.

2. Modify ``example_scripts/example_runScripts.py`` to run new problem
   set in ``fitbenchmarking/benchmark_problems/``.


.. _problem-types:

Adding additional fitting problem definition types
--------------------------------------------------

**Fitting problem definition types currently supported**

The types (formats) that are currently supported
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

To add a new fitting problem type, it is a requirement that the parser name
can be derived from the file to be parsed.
This is done for all current file formats by including it as the first line
in the file. e.g ``# Fitbenchmark Format`` or ``NIST/ITL StRD``.

To add a new fitting problem definition type, complete the following steps:

1. Give the format a name (``<format_name>``).
   This should be a single word or string of alphanumeric characters,
   and must be unique ignoring case.
2. Create a parser in the ``fitbenchmarking/parsing`` directory.
   This parser must satisfy the following:

   - Name of file should be of the form ``"<format_name>_parser.py"``
   - Parser must be a subclass of ``base_parser.Parser``
   - Parser must implement ``parse(self)`` method which takes only ``self``
     and returns a populated ``fitting_problem.FittingProblem``

   Note: File opening and closing is handled automatically.

3. If the format is unable to accomodate the current convention of
   starting with the ``<format_name>``, you will need to edit
   ``parser_factory.ParserFactory``.
   This should be done in such a way that the type is inferred from the file.
   e.g. If the type has a specific extension, the ``<format_name>`` could be
   made to match this, which future types could exploit.

4. Create the files to test the new parser.
   Automated tests are run against all parsers in FitBenchmarking,
   these work by using test files in
   ``fitbenchmarking/parsing/tests/<format_name>``.
   There are 2 types of test files needed:

   - **Generic tests**: 1 file must be provided in the directory for each file
     in ``fitbenchmarking/parsing/tests/expected/``.
     This file must be in the new file format and will be parsed using the new
     parser to check that the entries in the generated fitting problem match
     the values in the ``expected`` file.

   - **Function tests**: 1 file must be provided in the directory to test that
     function evaluation is as expected. This file must be in json format and
     contain a string of the form::

       {"file_name1": [[x1, [param11, param21], result1],
                       [x2, [param12, param22], result2],
                       ...],
       {"file_name2": [...],
        ...}``

     The test will then load the files in turn and run it against each item in
     the list, raising an issue if the result is not suitably close to the
     specified value.

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
   ``fitbenchmarking/fitbenchmark_one_problem.py``.
   For ease of maintainance, please add new controllers in alphabetical order.

3. Document the available minimizers (currently done by adding to
   ``fitbenchmarking/fitbenchmarking_default_options.json``)

4. Create tests for the software in
   ``fitbenchmarking/fitting/tests/test_controllers.py``.
   Again, for ease of maintainance, please add new controllers in alphabetical order.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.


