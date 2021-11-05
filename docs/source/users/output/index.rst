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
    :caption: Available tables:

    compare
    acc
    runtime
    local_min

Display modes
-------------

The tables for ``accuracy``, ``runtime`` and ``compare`` have three display modes:

.. prettyprintmodulevalue::
   :module: fitbenchmarking.results_processing.base_table
   :var: FORMAT_DESCRIPTION

This can be set in the option file using the :ref:`Comparison Mode <ComparisonOption>` option.

The :ref:`local_min` table is formatted differently, and doesn't use this convention.

Performance profile
-------------------

Below the table there is a performance profile.
This is documented in :ref:`performance_profile`

Support Pages
*************

In each of the tables, a support page for an individual result can be accessed
by clicking on the associated table cell. Clicking on a row header will open
a summary page for the problem as a whole.

.. toctree::
    :titlesonly:
    :maxdepth: 2
    :caption: Available Pages:

    support_pages
    problem_summary_pages
