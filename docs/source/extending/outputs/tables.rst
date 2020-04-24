.. _tables:

########################
Adding additional Tables
########################


*This section describes how to add additional tables to analyse the results from FitBenchmarking.*

The tables that are currently supported are:

- Combined table :class:`~fitbenchmarking.results_processing.compare_table.CompareTable`
- Accuracy table :class:`~fitbenchmarking.results_processing.acc_table.AccTable`
- Runtime table :class:`~fitbenchmarking.results_processing.runtime_table.RuntimeTable`
- Local minimiser table :class:`~fitbenchmarking.results_processing.local_min_table.LocalMinTable`

following members of the :class:`~fitbenchmarking.results_processing.base_table.Table` class:

In order to add a new table, you will need to:

1. Give the table a name `<table_name>` this will be used by users when
   selecting this output from FitBenchmarking.
2. Create ``fitbenchmarking/results_processing/<table_name>_table.py``
   which contains a new subclass of ``Table``
   (from ``base_table.py``).
   The main functions to change are:

   - ``get_values()``: This function processes the dictionary of results objects into values presented in the tables.
   - ``display_str()``: Converts the result from ``get_values()`` into a string representation used in the tables. The base class implementation, for example, takes a tuple of two dictionary's containing the absolute and relative values of the runtime results and combines them into a single sting.

   Additional functions to be changed are:

   - ``get_colour()``: Converts the result from ``get_colour()`` into the HTML colours used in the tables. The base class implementation, for example, uses the relative results and ``colour_scale`` within :class:`~fitbenchmarking.utils.options.Options`
   - ``colour_highlight()``: Takes the HTML colour values from ``get_colour()`` and maps it over the HTML table using the Pandas style mapper.

3. Documenting the new table class is done by setting the docstring to be
   the description of the class.

4. Create tests for the table in
   ``fitbenchmarking/results_processing/tests/test_tables.py``. Generate both
   a HTML and text table output as the expected result and add this to the
   tests.


The :class:`~fitbenchmarking.results_processing.base_table.Table` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See below for the description of the base class implementation of ``get_values()``, ``display_str()``, ``get_colour()`` and ``colour_highlight()``.

.. currentmodule:: fitbenchmarking.results_processing.base_table
.. autoclass:: fitbenchmarking.results_processing.base_table.Table
          :members: get_values, display_str, get_colour, colour_highlight
