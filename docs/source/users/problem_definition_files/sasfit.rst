.. _sasfit_format:

******************
SASfit File Format
******************

The SASfit file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

Examples of SASfit problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/SAS_modelling/SASfit/SANS_polymer_single.txt


As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software
  'sasfit' (case insensitive).

  **Licence** SASfit is available under a
  `GPL-3 Licence <https://github.com/SASfit/SASfit?tab=GPL-3.0-1-ov-file#>`_.

name, description, input_file, plot_scale
  As described in the native format.

function
  The function can be described by a series of SASfit functions (separated by a semi-colon),
  which are defined in the
  `SASfit manual <https://raw.githubusercontent.com/SASfit/SASfit/master/doc/manual/sasfit.pdf>`_.
  Please note that currently only form factors are supported, so size distributions and structure
  factors should not be included in the function string.
  Only parameters which are being fitted should be included in the function string.

fixed_params
  A list of parameters which should be fixed to a constant value.

  For a multifit problem, one set of fixed parameters may be given per
  dataset, separated by semi-colons. Every set must fix the same parameters,
  but each may fix them to different values, so that a parameter which the
  experiment fixes to a different value in each dataset can be held at its
  own value in each of them. The example below is a contrast variation
  series, in which the solvent scattering length density ``eta_solv`` is
  known and differs between the datasets, while the particle parameters are
  tied across them:

  .. literalinclude:: ../../../../examples/benchmark_problems/SAS_modelling/SASfit/SANS_cv_STJ1.txt