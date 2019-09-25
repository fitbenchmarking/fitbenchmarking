.. _examples:

Examples
========

The file ``example_runScript.py`` can be found in the
``fitbenchmarking/example_scripts/`` directory. It was written to provide
any potential users with an example of how FitBenchmarking is run.

To run this script using its basic settings, please follow
the :ref:`getting-started`
page. This page is
for giving an overview of how the script works.

The benchmarking starts by considering two problem sets (neutron and
NIST). Each provided problem is fitted using all the available
minimizers in `Mantid <http://www.mantidproject.org/Main_Page>`__, a
comprehensive data analysis software. FitBenchmarking records the time
it took for a certain minimizer to solve a certain fitting problem.
Additionally, the accuracy of the solution is also recorded by
performing a
`chi-squared <https://en.wikipedia.org/wiki/Chi-squared_test>`__ test of
the fit. After running through all the problems, accuracy and runtimes
tables are created for each problem set. In essence, there will be two
tables for neutron data and two for NIST data. These tables are saved in
the ``fitbenchmarking/example_scripts/results`` folder.

The final result table for neutron looks like this:

.. figure:: ../../images/example_table.png
   :alt: Result Table

   Result Table

The ``example_runScript.py`` file is heavily commented. If you want to
learn more about how it works and how can he modifty it, please consult
the file itself using a text editor.
