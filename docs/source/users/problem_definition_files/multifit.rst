.. _multifit:

************************************
Native File Format (Mantid MultiFit)
************************************

In FitBenchmarking, the native file format combines parsers for Mantid and
SASView problems.

As part of the Mantid parsing we also offer limited support for Mantids
`MultiFit <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html?highlight=fit#multiple-fit>`__
functionality.

This document will focus on MultiFit, in which some options differ from single
fit problems.
For information on the single fit problems, see :ref:`native`.

**Note: Due to the way Mantid uses ties (a central feature of MultiFit),
MultiFit problems can only be used with Mantid minimizers.**

In this format, data is separated from the function. This allows running the
same dataset against multiple different models to assess which is the most
appropriate.

An example of a native problem is:

.. literalinclude:: ../../../../examples/benchmark_problems/MultiFit/MUSR62260.txt


This example shows the basic structure in which the file starts with a comment
indicating it is a FitBenchmark problem followed by key-value pairs. Available
keys are described below:

software
========
Either 'Mantid' or 'SasView' (case insensitive).
This defines which of the software to use to generate the function to be used
in fitting.

name
====
The name of the problem.
This will be used as a unique reference so should not match other names in the
dataset. A sanitised version of this name will also be used in filenames with
commas stripped out and spaces replaced by underscores.

description
===========
A description of the dataset.
This is currently unused within FitBenchmarking, but can be useful for
explaining problems, and is intended to be added to results pages in the
future.

input_file
==========
The names of the files containing the data to fit.
This indicates that the input is MultiFit if it contains a list of file names.
If only a single name is passed, the problem does not use MultiFit.

The files must be in a `data_files` directory, and should have the form::

   header

   x1 y1 [e1]
   x2 y2 [e2]
   ...

where Mantid uses the convention of ``# X Y E`` although this is not enforced.
The error column is optional in this format.

function
========
This defines the function that will be used as a model for the fitting.

In FitBenchmarking, any function that can be specified for the 'Mantid'
software option can be used with MultiFit as the boilerplate parts of the
function are done automatically.

When fitting, this function will be used for each of the input_files given
simultaneously.

A Mantid funtion consists of one or more functions separated by a semicolon.
This allows for a powerful way of describing problems, which may have multiple
aspects such as more than one gausian and a linear background.

To use one of the base functions in Mantid, please see the list available
`here <https://docs.mantidproject.org/nightly/fitting/fitfunctions/categories/FitFunctions.html>`__.

ties
====
This entry is used to define global variables by tieing a variable across
input files.

Each string in the list should reference a parameter in the function using
Mantids convention of ``f<i>.<name>`` where ``i`` is the position of the
function in the function string, and ``name`` is the global parameter.

For example to run a fit which has a shared background and peak height,
the function and ties fields might look like::

   function='name=LinearBackground, A0=0, A1=0; name=Gaussian, Height=0.01, PeakCentre=0.00037, Sigma=1e-05'
   ties=['f0.A0', 'f0.A1', 'f1.Height']

fit_ranges
==========
This specifies the region to be fit and takes the form shown in the example.
Here the first number in each range is a minimum and the second is a maximum.
