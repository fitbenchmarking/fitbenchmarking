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

Accessing plots of fit
**********************

In each of the tables, more information about the fit (including parameter values and plots of fit)
for an individual result can be accessed by clicking on the associated table cell.

Please note that in order to view the plots of fit, the :ref:`Make Plots <MakePlots>` option must be
set to ``True``.

Table formats
*************

The tables for ``accuracy``, ``runtime`` and ``compare`` have three display modes:

.. prettyprintmodulevalue::
   :module: fitbenchmarking.results_processing.base_table
   :var: FORMAT_DESCRIPTION

This can be set in the option file using the :ref:`Comparison Mode <ComparisonOption>` option.

The :ref:`local_min` table is formatted differently, and doesn't use this convention.

