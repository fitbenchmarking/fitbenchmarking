.. _native:

******************
Native File Format
******************

In FitBenchmarking, the native file format is used to read Mantid and
SASView problems.

In this format, data is separated from the function. This allows running the
same dataset against multiple different models to assess which is the most
appropriate.

An example of a native problem is:

.. literalinclude:: ../../../../examples/benchmark_problems/Muon/Muon_HIFI_113856.txt


This example shows the basic structure in which the file starts with a comment
indicating it is a FitBenchmark problem followed by key-value pairs. Available
keys are described below:

software
  Either 'Mantid' or 'SasView' (case insensitive).
  
  This defines whether to use Mantid or SasView to generate the model.
  The 'Mantid' software also supports Mantid's MultiFit functionality, which
  requires the parameters listed here to be defined slightly differently.
  More information can be found in :ref:`multifit`.

name
  The name of the problem.

  This will be used as a unique reference so should not match other names in the
  dataset. A sanitised version of this name will also be used in filenames with
  commas stripped out and spaces replaced by underscores.

description
  A description of the dataset.

  This is currently unused within FitBenchmarking, but can be useful for
  explaining problems.

input_file
  The name of a file containing the data to fit.

  The file must be in a subdirectory named `data_files`, and should have the form::

     header

     x1 y1 [e1]
     x2 y2 [e2]
     ...

  Mantid uses the convention of ``# X Y E`` as the header and SASView uses
  the convention ``<X>   <Y>   <E>``, although neither of these are enforced.
  The error column is optional in this format.

function
  This defines the function that will be used as a model for the fitting.

  Inside FitBenchmarking, this is passed on to the specified software and, as
  such, the format is specific to the package we wish to use, as described below.

  **Mantid**

  A Mantid function consists of one or more base functions separated by a semicolon.
  This allows for a powerful way of describing problems, which may have multiple
  components such as more than one Gaussian and a linear background.

  To use one of the base functions in Mantid, please see the list available
  `here <https://docs.mantidproject.org/nightly/fitting/fitfunctions/categories/FitFunctions.html>`__.

  *Note: Any non-standard arguments (e.g. ties, constraints, fixes, ...) will
  only work with Mantid fitting software. Using other minimizers to fit these
  problems will result in the non-standard arguments being ignored.*

  **SASView**

  SASView functions can be any of
  `these <https://www.sasview.org/docs/user/sasgui/perspectives/fitting/models/index.html>`__.

fit_ranges
  This specifies the region to be fit.

  It takes the form shown in the example, where the first number
  is the minimum in the range and the second is the maximum.
