.. _mantid_file:

******************
Mantid File Format
******************

Mantid supports all the functionality the :ref:`native`. The same
features can be used to set up fitting problems. 

  .. note::
    However, The Mantid file format also supports **Multifit** and **Multistart** functionality,
    which requires additional parameters to be defined.

    More information can be found in the **Multifit** and the **Multistart** sections below.

Native Fitting Format
=====================

Example of mantid problems defined using native fitting are:

.. literalinclude:: ../../../../examples/benchmark_problems/Muon/Muon_HIFI_113856.txt
.. literalinclude:: ../../../../examples/benchmark_problems/Neutron/ENGINX193749_calibration_peak5.txt

These examples show the native format using key-value pairs.
Available keys for the native format are described below:

software
  'Mantid' (case insensitive).

  **Licence** Mantid is available under a
  `GPL-3 Licence <https://github.com/mantidproject/mantid/blob/master/LICENSE.txt>`_.

name
  As in :ref:`native`.

description
  As in :ref:`native`.

input_file
  It specifies the name of the file(s) containing the data to fit.

  The data file is usually placed in a subdirectory named ``data_files``, and should have the form::

    # X Y E

     x11 [x12 [x13 ...]] y11 [y12 [y13 ...]] [e11 [e12 ...]]
     x21 [x22 [x23 ...]] y21 [y22 [y23 ...]] [e21 [e22 ...]]
     ...

plot_scale
  As in :ref:`native`.

function
  A Mantid function consists of one or more base functions separated by a semicolon.
  This allows for a powerful way of describing problems, which may have multiple
  components such as more than one Gaussian and a linear background.

  To use one of the base functions in Mantid, please see the list available
  `here <https://docs.mantidproject.org/nightly/fitting/fitfunctions/categories/FitFunctions.html>`__.

  .. warning::

    Any non-standard arguments (e.g. ties, constraints, fixes, ...) will
    only work with Mantid fitting software. Using other minimizers to fit these
    problems will result in the non-standard arguments being ignored.

jacobian
  As in :ref:`native`.

fit_ranges
  As in :ref:`native`.

parameter_ranges
  As in :ref:`native`.


Multifit Analysis
=================

As part of the Mantid parsing we also offer limited support for Mantid's
`MultiFit <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html?highlight=fit#multiple-fit>`__
functionality.

In this section, we outline how to use Mantid's MultiFit feature,
in which some options differ from the **native** :ref:`mantid_file`.

.. warning::
   Due to the way Mantid uses ties (a central feature of MultiFit),
   MultiFit problems can only be used with Mantid minimizers.

In this format, data is separated from the function. This allows running the
same dataset against multiple different models to assess which is the most
appropriate.

An example of a multifit problem is:

.. literalinclude:: ../../../../examples/benchmark_problems/MultiFit/MUSR62260.txt

Below we outline the differences between this format and the **native** :ref:`mantid_file`.

input_file
  You must pass in a list of data files (see above example).

function
  As in **native** :ref:`mantid_file`.
  
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


Multistart Analysis
===================

Mantid also supports multistart analysis. This functionalty allows multiple datasets with different
starting values for the fitting parameters to be defined from the same problem definition file. 

An example of multi-start problem defination is:

.. literalinclude:: ../../../../examples/benchmark_problems/synthetic_data/backtobackexp/b2b_exp.txt

Below we outline the differences between this format and the **native** :ref:`mantid_file`.

n_fits
  This is defined as an integer. It determines the number of
  datasets that will be created with varying starting values (see above example).

function
  The function needs to be defined with placeholders.
  The first part of the placeholder contains the function index in lowercase.
  The second part of the placeholder is the name of the parameter.
  This is case sensitive and should be defined in the case used in the Mantid software.
  The placeholders must also be enclosed in curly braces.

  For example, a valid function defination for multi-start analysis is::

     function = 'name=Gaussian, Height={f0.Height}, PeakCentre={f0.PeakCentre}, Sigma={f0.Sigma} ; name=FlatBackground, A0={f1.A0}'

parameter_means
  This is defined as a string of parameter names and their mean values.
  These are used as the mean values of the Gaussian distribution from which the
  starting values are sampled.

  For example, a valid syntax is::

     parameter_means = 'f0.Height=10, f0.PeakCentre=7, f0.Sigma=0.7, f1.A0=0'

parameter_sigmas
  This is defined as a string of parameter names and their sigma values.
  These are used as the standard deviations of the Gaussian distribution
  from which the starting values are sampled.

  For example, a valid syntax is::

     parameter_sigmas = 'f0.Height=3, f0.PeakCentre=2, f0.Sigma=0.5, f1.A0=1'

seed
  This is an optional argument that can be used to provide a seed to create reproducible results (see above example).