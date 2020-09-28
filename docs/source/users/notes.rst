.. _notes:

############
Known Issues
############

This page is used to detail any known issues or unexpected behaviour
within the software.


************************************
Problem-Format/Software Combinations
************************************

When comparing minimizer options from one software package
(e.g., comparing all `scipy_ls` minimizers), we are not aware of any issues.
However, the general problem of comparing minimizers from multiple software
packages, and with different problem-formats, on truely equal terms is harder to
achieve.

The following list details all cases where we are aware of a possible bias:

- **Using native FitBenchmarking problems with the Mantid software and fitting using Mantid.**

  With Mantid data, the function evaluation is slightly faster for Mantid minimizers
  than for all other minimizers. You should account for this when interpreting the
  results obtained in this case.

- **Using ties in native FitBenchmarking problems with the Mantid software.**

  This is not available for non-Mantid fitting software.
  In these cases, a warning will be generated.


In all cases, the stopping criterion of each minimizer is set to the default
value.
An experienced user can change this.
