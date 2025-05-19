.. _bal_format:

****************
BAL File Format
****************

The Bundle Adjustment in the Large (BAL) file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

Examples of HOGBEN problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/Bundle_Adjustment/Ladybug.txt

.. literalinclude:: ../../../../examples/benchmark_problems//Bundle_Adjustment/Trafalgar.txt

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software, name, description
  As described in the native format.

input_file
  The input file should be in bz2 format and contains all information needed to parse the problem.
  A selection of data files can be found on the `GRAIL website <https://grail.cs.washington.edu/projects/bal/>`_. 
