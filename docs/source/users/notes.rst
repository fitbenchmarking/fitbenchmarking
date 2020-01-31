.. _notes:

#####
Notes
#####

This document is used to detail any known issues or unexpected behaviour
within the software.


************************************
Problem-Format/Software Combinations
************************************

When comparing the minimizers of a particular software against a particular type of problem-format files we are not aware of any issues. However, the general problem of comparising minimizers from different software and with different problem-formats - all on truely equal terms - is harder to achieve. In the table below, the cells with a value different from None, show the cases, that we are aware off, where this is still not achieved.

.. list-table::
   :widths: 1 1 3 1 3 1
   :stub-columns: 1
   :header-rows: 1

   * - Problem Types \\ Fitting Software
     - DFOGN
     - Mantid
     - RALFit
     - SASView
     - Scipy
   * - Fitbenchmark
     - None
     - | This is expected to have a smaller
       | overhead on evaluating functions,
       | and so may be faster when compared
       | to other softwares.
     - None
     - None
     - None
   * - SASView
     - None
     - None
     - None
     - None
     - None
   * - NIST
     - None
     - None
     - None
     - None
     - None

The stopping criterion of each minimizer is set to the default value.
An experienced user can change this.
