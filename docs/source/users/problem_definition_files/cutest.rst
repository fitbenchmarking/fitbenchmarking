##################
CUTEst File Format
##################

The CUTEst file format is based on the SIF format, and in FitBenchmarking, all
SIF files are assumed to be CUTEst problems.

The SIF file format is very powerful, and CUTEst will work with arbitrary
variable names, however for FitBenchmarking, these must match a set of expected
variable names.

Defining Data
*************

Data should be defined using the format of::

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
******************

For the free variables in functions, we use the convention of::

     IE N             <num_vars>

This is used to tell FitBenchmarking how many degrees of freedom need to be
fit.
In some cases variables will be vectors, and the number of degrees of freedom
will be greater, most problems use ``NVEC`` as a convention to input the number
of vectors.
