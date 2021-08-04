====================
 CUTEst File Format
====================

The CUTEst file format in FitBenchmarking is a slight modification of the
`SIF format <http://www.numerical.rl.ac.uk/lancelot/sif/sif.html>`_.
Specifically, the data points, errors, and the number of variables
must be defined in such a way to allow FitBenchmarking to access this data; see below.
In FitBenchmarking, all SIF files are assumed to be CUTEst problems.

These problems are a subset of the problems in the
`CUTEr/st Test Problem Set <http://www.cuter.rl.ac.uk/Problems/mastsif.shtml>`_,
which may have been adapted to work with FitBenchmarking.

The SIF file format is very powerful, and CUTEst will work with arbitrary
variable names, however for FitBenchmarking, these must match a set of expected
variable names.

**Licence** This file format needs PyCUTEst and the packages ARCHDefs, CUTEst and
SIFDECODE to be installed.
PyCUTEst is available under the
`GPL-3 <https://github.com/jfowkes/pycutest/blob/master/LICENSE>`__ licence.
`ARCHDEFS <https://github.com/ralna/ARCHDefs/blob/master/LICENSE>`__,
`CUTEst <https://github.com/ralna/CUTEst/blob/master/LICENSE>`__ and
`SIFDECODE <https://github.com/ralna/SIFDecode/blob/master/LICENSE>`__
are available under an LGPL (v2.1 or later) licence.

Modifications to the SIF format for FitBenchmarking problems
============================================================

In order for FitBenchmarking to access the data, the SIF files must
be written using the following conventions.

Defining Data
-------------

Data should be defined using the format::

     RE X<idx>        <val_x>
     RE Y<idx>        <val_y>
     RE E<idx>        <val_error>

where ``<idx>`` is the index of the data point, and ``<val_x>``, ``<val_y>``,
and ``<val_error>`` are the values attributed to it.

Usually, ``<idx>`` will range from 1 to ``<num_x>``, with that defined as::

     IE M             <num_x>

If ``<idx>`` does not start at 1, the following lines can be used to specify
the range::

     IE MLOWER        <min_idx>
     IE MUPPER        <max_idx>

Defining Variables
------------------

For the free variables in functions, we use the convention::

     IE N             <num_vars>

This is used to tell FitBenchmarking how many degrees of freedom we need to
fit.
In some cases variables will be vectors, and the number of degrees of freedom
will be greater, most problems use ``NVEC`` as a convention to input the number
of vectors.

Support for Bounds
==================

Parameter ranges can be added to SIF files using the `BOUNDS <https://www.numerical.rl.ac.uk/lancelot/sif/node26.html>`_
indicator card.

Currently in Fitbenchmarking, problems with parameter ranges can be handled by SciPy, Bumps, Minuit, Mantid,
Matlab Optimization Toolbox, DFO, Levmar and RALFit fitting software. Please note that the following Mantid
minimizers currently throw an exception when parameter ranges are used: BFGS, Conjugate gradient
(Fletcher-Reeves imp.), Conjugate gradient (Polak-Ribiere imp.) and SteepestDescent.
