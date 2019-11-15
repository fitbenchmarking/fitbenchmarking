.. _notes:

#####
Notes
#####

This document is used to detail any known issues or unexpected behaviour
within the software.


************************************
Problem-Format/Software Combinations
************************************

Some of the pairings of problem types and software exhibit behavour which may
be unexpected.
These are listed in the below table.

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
     - | This is known to display a large
       | amount of exceptions relating to
       | setting values to inf.
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

The stopping criterion of each minimizer is set to the default value. An experienced user can change this.

**************************
SASView Problem Definition
**************************
Due to the physical expectation for problems in the SASView data format, all
data with an x value of 0 will be removed from the dataset before fitting.
