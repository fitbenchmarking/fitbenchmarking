.. _multifit:

************************************
Native File Format (Mantid MultiFit)
************************************

As part of the Mantid parsing we also offer limited support for Mantid's
`MultiFit <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html?highlight=fit#multiple-fit>`__
functionality.

Here we outline how to use Mantid's MultiFit with FitBenchmarking,
in which some options differ from the standard  :ref:`native`.

.. warning::
   Due to the way Mantid uses ties (a central feature of MultiFit),
   MultiFit problems can only be used with Mantid minimizers.

In this format, data is separated from the function. This allows running the
same dataset against multiple different models to assess which is the most
appropriate.

An example of a multifit problem is:

.. literalinclude:: ../../../../examples/benchmark_problems/MultiFit/MUSR62260.txt


Below we outline the differences between this and the :ref:`native`.

software
  Must be `Mantid`.

name
  As in :ref:`native`.

description
  As in :ref:`native`.

input_file
  As in :ref:`native`, but you must pass in a list of
  data files (see above example).

function
  As in :ref:`native`.
  
  When fitting, this function will be used for each of the ``input_files`` given
  simultaneously.

ties
  This entry is used to define global variables by tieing a variable across
  input files.

  Each string in the list should reference a parameter in the function using
  Mantid's convention of ``f<i>.<name>`` where ``i`` is the position of the
  function in the function string, and ``name`` is the global parameter.

  For example to run a fit which has a shared background and peak height,
  the function and ties fields might look like::

     function='name=LinearBackground, A0=0, A1=0; name=Gaussian, Height=0.01, PeakCentre=0.00037, Sigma=1e-05'
     ties=['f0.A0', 'f0.A1', 'f1.Height']

fit_ranges
  As in :ref:`native`.
