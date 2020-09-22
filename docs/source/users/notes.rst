.. _notes:

#####
Notes
#####

This document is used to detail any known issues or unexpected behaviour
within the software.


************************************
Problem-Format/Software Combinations
************************************

When comparing the minimizers of a particular software against a particular
type of problem-format files we are not aware of any issues.
However, the general problem of comparing minimizers from different software
and with different problem-formats - all on truely equal terms - is harder to
achieve.

The following list details all cases where we are aware of a possible bias:

- Using native FitBenchmarking problems with the Mantid software and fitting using Mantid.
    This is expected to have a smaller overhead on evaluating
    functions, and so may be marginally faster when compared to other
    software.
- Using ties in native FitBenchmarking problems with the Mantid software.
    This is not available for non-Mantid fitting software.
    In these cases, a warning will be generated.


In all cases, the stopping criterion of each minimizer is set to the default
value.
An experienced user can change this.


*******
Parsers
*******

The CUTEst parser is known to give several warnings about implicitly deleting
temporary directories. This is expected and will not affect the results.
