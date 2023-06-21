.. _output:

######################
FitBenchmarking Output
######################

FitBenchmarking produces tables and reports called support pages as outputs.
The links below give descriptions of these outputs.

Tables
******

.. toctree::
    :titlesonly:
    :maxdepth: 2

    compare
    acc
    runtime
    local_min
    emissions

Display modes
-------------

The tables for ``accuracy``, ``runtime``, ``emissions``, and ``compare`` have three display
modes:

.. prettyprintmodulevalue::
   :module: fitbenchmarking.results_processing.base_table
   :var: FORMAT_DESCRIPTION

This can be set in the option file using the
:ref:`Comparison Mode <ComparisonOption>` option.

The :ref:`local_min` table is formatted differently, and doesn't use this
convention.

Performance profile
-------------------

Below the table there is a :ref:`performance_profile`.

Support Pages
*************

In each of the tables, a :ref:`fitting_report` for an individual result can be accessed
by clicking on the associated table cell. Clicking the problem name at the
start of a row will open a :ref:`problem_summary_page` for the problem as a whole.

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    fitting_report
    problem_summary_pages
