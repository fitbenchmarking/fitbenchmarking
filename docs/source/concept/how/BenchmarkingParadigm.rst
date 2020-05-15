.. _BenchmarkingParadigm:

*************************
The Benchmarking Paradigm
*************************

      
Once you have chosen which minimizers you want to compare on which problems,
running FitBenchmarking will give you a comparison to indicate which of the
chosen minimizers performs best.

There are a number of options that you can pick to customize what your tests
are comparing or how they are run.  A full list of these options, and how to
select them, is given in the section :ref:`options`.

FitBenchmarking creates tables, as given in the section :ref:`output`,
which show a comparison between the different minimizers available.
An example of a table is:

.. figure:: ../../../images/example_table.png
   :alt: Example Table

This is the result of fitbenchmarking mantid on a set of neutron data.
Both chi squared values and values that are normalised with respect
to the best minimizer per problem are given.
The problem names link to html pages that display plots of the
data and the fit that was performed, together with initial and final
values of the parameters. Here is an example of the final plot fit:

.. figure:: ../../../images/example_plot.png
   :alt: Example Plot
