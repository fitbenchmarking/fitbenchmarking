.. _extending-fitbenchmarking:

#########################
Extending Fitbenchmarking
#########################

.. _problem-groups:

Adding additional problem groups
--------------------------------

*This section describes how to add a problem group to the fit benchmarking
software. The default problem groups that come with this software are:
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

The types (formats) that are currently supported are:

  - Native (Fitbenchmark)
    This supports functions/data from Mantid or SasView
  - NIST

An example of these formats can be seen in
``benchmark_problems/Neutron_data/``/``benchmark_problems/SAS_modelling/``
and ``benchmark_problems/NIST/`` respectively.

**Adding new fitting problem definition types**

To add a new fitting problem type, it is a requirement that the parser name
can be derived from the file to be parsed.
This is done for all current file formats by including it as the first line
in the file. e.g ``# Fitbenchmark Problem`` or ``NIST/ITL StRD``.

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

3. If the format is unable to accommodate the current convention of
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

   - **Function tests**: 1 file can be provided in the directory to test that
     function evaluation is as expected. This file must be in json format and
     contain a string of the form::

       {"file_name1": [[x1, [param11, param21], result1],
                       [x2, [param12, param22], result2],
                       ...],
       {"file_name2": [...],
        ...}

     The test will then load the files in turn and run it against each item in
     the list, raising an issue if the result is not suitably close to the
     specified value.

   - **Integration tests**: Add an example to the `mock_problems/all_parser_test_set`.
     This will be used to verify that the problem can be run by scipy, and that
     accuracy results do not change unexpectedly in future changes to the code.

     As part of this, the `systests/expected/parsers.txt` file will need to be
     updated. This is done by running the systests::

       pytest fitbenchmarking/systests

     and then checking that the only difference between the results table and the
     expected value is the new problem, and replacing the expected with the result.

5. Verify that your tests have been found by running
   `pytest -vv fitbenchmarking/parsing/tests/test_parsers.py`

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

Fitting software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to add a new controller, you will need to:

1. Give the software a name `<software_name>` this will be used by users when
   selecting this software.
2. Create ``fitbenchmarking/fitting/controllers/<software_name>_controller.py``
   which contains a new subclass of ``BaseSoftwareController``
   (from ``base_controller.py``).
   This should implement 4 functions:

   -  ``__init__()``: Initialise anything that is needed specifically for the
      software, do any work that can be done without knowledge of the
      minimizer to use, or function to fit, and call ``super().__init__()``.
   -  ``setup()``: Do any work that must be done only after knowing the
      minimizer to use and the function to fit. E.g. creating function wrappers
      around a callable.
   -  ``fit()``: Run the fitting. This will be timed so should include only
      what is needed to fit the data.
   -  ``cleanup()``: Convert the results into the expected numpy arrays,
      error flags and store them in the results variables
      (``self.results``, ``self.final_params``, ``self.flag``).
      The flag corresponds to the following messages::

         0: "Successfully converged",
         1: "Software reported maximum number of iterations exceeded",
         2: "Software run but didn't converge to solution",
         3: "Software raised an exception".

4. Document the available minimizers (currently done by adding to
   ``fitbenchmarking/utils/default_options.ini`` and any example files in
   the ``example_scripts`` directory)

5. Create tests for the software in
   ``fitbenchmarking/fitting/tests/test_controllers.py``.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.

.. note::
   For ease of maintenance, please add new controllers to a list of software in alphabetical order.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new minimizers, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` class:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
   :members: eval_f, eval_r, eval_r_norm, eval_j,
	     data_x, data_y, data_e, starting_values

