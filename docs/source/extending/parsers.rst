.. _parsers:

#######################################
Adding Fitting Problem Definition Types
#######################################

The problem definition types we currently support are listed in the page :ref:`problem_def`.

To add a new fitting problem type, the parser name
must be derived from the file to be parsed.
For current file formats by including it as the first line
in the file. e.g ``# Fitbenchmark Problem`` or ``NIST/ITL StRD``, or by checking
the file extension.

To add a new fitting problem definition type, complete the following steps:

1. Give the format a name (``<format_name>``).
   This should be a single word or string of alphanumeric characters,
   and must be unique ignoring case.
2. Create a parser in the ``fitbenchmarking/parsing`` directory.
   This parser must satisfy the following:

   - The filename should be of the form ``"<format_name>_parser.py"``
   - The parser must be a subclass of the base parser, :class:`~fitbenchmarking.parsing.base_parser.Parser`
   - The parser must implement ``parse(self)`` method which takes only ``self``
     and returns a populated :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`

   Note: File opening and closing is handled automatically.

3. If the format is unable to accommodate the current convention of
   starting with the ``<format_name>``, you will need to edit
   :class:`~fitbenchmarking.parsing.parser_factory.ParserFactory`.
   This should be done in such a way that the type is inferred from the file.

4. Create the files to test the new parser.
   Automated tests are run against the parsers in FitBenchmarking,
   which work by using test files in
   ``fitbenchmarking/parsing/tests/<format_name>``.
   In the :meth:`test_parsers.generate_test_cases` function,
   one needs to add the new parser's
   name to the variable ``formats``,
   based on whether or not the parser is ``pip`` installable.
   There are 2 types of test files needed:

   - **Generic tests**: ``fitbenchmarking/parsing/tests/expected/`` contains
     two files, ``basic.json`` and ``start_end_x.json``.
     You must write two input files in the new file format,
     which will be parsed using the new parser to check that the entries
     in the generated fitting problem match the values expected.
     These must be called ``basic.<ext>``, ``start_end_x.<ext>``, where ``<ext>``
     is the extension of the new file format, and they must be placed in
     ``fitbenchmarking/parsing/tests/<format_name>/``.

   - **Function tests**: A file named ``function_evaluations.json``
     must also be provided in
     ``fitbenchmarking/parsing/tests/<format_name>/``, which tests that the
     function evaluation behaves as expected. This file must be in json format and
     contain a string of the form::

       {"file_name1": [[[x11,x12,...,x1n], [param11, param12,...,param1m], [result11,result12,...,result1n]],
                       [[x21,x22,...,x2n], [param21, param22,...,param2m], [result21,result22,...,result2n]],
                       ...],
       {"file_name2": [...],
        ...}

     The test will then parse the files ``file_name<x>`` in turn evaluate the function
     at the given ``xx`` values and ``params``. If the result is not suitably close to
     the specified value the test will fail.

   - **Integration tests**: Add an example to the directory
     ``fitbenchmarking/mock_problems/all_parser_set/``.
     This will be used to verify that the problem can be run by scipy, and that
     accuracy results do not change unexpectedly in future updates.
     If the software used for the new parser is pip-installable, and the
     installation is done via FitBenchmarking's ``setup.py``, then add the
     same example to ``fitbenchmarking/mock_problems/default_parsers/``.

     As part of this, the ``systests/expected_results/all_parsers.txt`` file,
      and if neccessary the ``systests/expected_results/default_parsers.txt`` file,
      will need to be updated. This is done by running the systests::

       pytest fitbenchmarking/systests

     and then checking that the only difference between the results table and the
     expected value is the new problem, and updating the expected file with the result.

5. Verify that your tests have been found and are successful by running
   `pytest -vv fitbenchmarking/parsing/tests/test_parsers.py`
