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
packages, and with different problem-formats, on truly equal terms is harder to
achieve.

The following list details all cases where we are aware of a possible bias:

- **Using native FitBenchmarking problems with the Mantid software and fitting using Mantid.**

  With Mantid data, the function evaluation is slightly faster for Mantid minimizers
  than for all other minimizers. You should account for this when interpreting the
  results obtained in this case.

- **Using non-scalar ties in native FitBenchmarking problems with the Mantid software.**

  Mantid allows parameters to be tied to expressions - e.g. X0=5.0 or X0=X1*2.
  While scalar ties are now supported for all minimizers the more complicated
  expressions are not supported. If you need this feature please get in touch
  with the development team with your use case.

- **Running Mantid problems with Matlab fitting software.**

  To run problems with Matlab fitting software through FitBenchmarking, within
  the Matlab Controller the dynamically created `cost_func.eval_model` function
  is serialized and then loaded in the Matlab Engine workspace. However for
  Mantid problems, this function is not picklable resulting in the problem
  being skipped over.

- **Running Mantid problems with NLOpt fitting software.**

  Our regression tests highlighted that the fit fails for all Mantid problems when
  using NLOpt. We are still investigating the cause of this.
  Details can be found in the associated
  `issue <https://github.com/fitbenchmarking/fitbenchmarking/issues/1366>`__.

- **Running Mantid problems with LMFit fitting software.**

  Our regression tests highlighted a reduced accuracy in solution of our test Mantid
  problem when using LMFit. We are still investigating the cause of this.
  Details can be found in the associated
  `issue <https://github.com/fitbenchmarking/fitbenchmarking/issues/1366>`__.

In all cases, the stopping criterion of each minimizer is set to the default
value.
An experienced user can change this.


***************************************
Specific Problem/Minimizer Combinations
***************************************

- **CrystalField Example with Mantid - DampedGaussNewton Minimizer.**

  With this combination, GSL is known to crash during Mantid's fitting.
  This causes python to exit without completing any remaining runs or
  generating output files.
  More information may be available via
  `the issue on Mantid's github page <https://github.com/mantidproject/mantid/issues/31176>`__.
