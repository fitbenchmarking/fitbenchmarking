.. _output:

######################
FitBenchmarking Output
######################

FitBenchmarking produces tables as outputs.  The links below give
descriptions of these tables.

.. toctree::
    :titlesonly:
    :maxdepth: 2
    :caption: Tables:

    compare
    acc
    runtime
    local_min

Table formats
*************

The tables for ``accuracy``, ``runtime`` and ``compare`` have three display modes:

.. prettyprintmodulevalue::
   :module: fitbenchmarking.results_processing.base_table
   :var: FORMAT_DESCRIPTION

This can be set in the option file using the :ref:`Comparison Mode <ComparisonOption>` option.

The :ref:`local_min` table is formatted differently, and doesn't use this convention.

