.. _tables:

#####################
Adding further Tables
#####################


The tables that are currently supported are listed in :ref:`output`.
In order to add a new table, you will need to:

1. Give the table a name ``<table_name>``. This will be used by users when
   selecting this output from FitBenchmarking.
2. Create ``fitbenchmarking/results_processing/<table_name>_table.py``
   which contains a new subclass of
   :class:`~fitbenchmarking.results_processing.base_table.Table`.
   The main functions to change are:

   - .. automethod:: fitbenchmarking.results_processing.base_table.Table.get_values
        :noindex:

   - .. automethod:: fitbenchmarking.results_processing.base_table.Table.display_str
        :noindex:

   Additional functions to be changed are:

   - .. automethod:: fitbenchmarking.results_processing.base_table.Table.get_colour
        :noindex:


         
   - .. automethod:: fitbenchmarking.results_processing.base_table.Table.colour_highlight
        :noindex:

3. Extend the ``table_type`` option in ``PLOTTING`` following the instructions in
   :ref:`options_extend`.
	   
4. Document the new table class is by setting the docstring to be
   the description of the table, and add to :ref:`output`.
   
5. Create tests for the table in
   ``fitbenchmarking/results_processing/tests/test_tables.py``. This is done
   by generating, ahead of time using the results problems constructed in
   ``fitbenchmarking/results_processing/tests/test_tables.generate_mock_results``, both a HTML and text table output as the expected
   result and adding the new table name to the global variable
   ``SORTED_TABLE_NAMES``. This will automatically run the comparison tests for the tables.

