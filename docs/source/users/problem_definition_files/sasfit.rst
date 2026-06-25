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
  Only parameters which are being fitted should be included in the function string.

fixed_params
  A list of parameters which should be fixed to a constant value.