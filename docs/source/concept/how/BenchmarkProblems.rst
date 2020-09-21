.. _BenchmarkProblems:

##################
Benchmark problems
##################

To help choose between the different minimizers, FitBenchmarking
comes with some curated Benchmark problems—although it’s straightforward
add custom data sets to the benchmark, if that is more appropriate; see
:ref:`problem_def` for specifics of how to add additional problems in a
supported file format.

We supply some standard nonlinear least-squares test problems in the
form of the `NIST nonlinear regression set <https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`_
and the relevant problems from the `CUTEst problem set <https://github.com/ralna/CUTEst/wiki>`_,
together with some real-world 
data sets that have been extracted from `Mantid <https://www.mantidproject.org>`__ and
`SASView <https://www.sasview.org>`__ usage examples and system tests.
We've made it possible to extend this list by following the steps in 
:ref:`controllers`.

Each of the test problems contain:

* a data set consisting of points :math:`(x_i, y_i)` (with optional errors on :math:`y_i`, :math:`\sigma_i`)
* a definition of the fitting function, :math:`f({\boldsymbol{\beta}};x)`
* (at least) one set of initial values for the function parameters :math:`{\boldsymbol{\beta}}_0`, and
* an optional set of target values that the parameters are expected to reach, :math:`{\boldsymbol{\beta}}_*`.

If a problem doesn’t have observational
errors (e.g., the NIST problem set), then FitBenchmarking can
approximate errors by taking :math:`\sigma_i = \sqrt{y_i}`.
Alternatively, there is an option to disregard errors and solve the
unweighted nonlinear least-squares problem, setting
:math:`\sigma_i = 1.0` irrespective of what has been passed in with the
problem data.

As we work with scientists in other areas, we will extend the problem
suite to encompass new categories. The FitBenchmarking framework has
been designed to make it easy to integrate new problem sets, and any
new problem set added to the framework can be tested with any and all of
the available fitting methods.

Currently FitBenchmarking ships with data from the following sources:

Powder Diffraction Data (SIF files)
-----------------------------------

In the folder `examples/benchmark_problems/DIAMOND_SIF` you will find
data from powder diffraction experiments.  The data supplied comes
from the `I14 Hard X-Ray Nanoprobe <https://www.diamond.ac.uk/Instruments/Imaging-and-Microscopy/I14.html>`_ beamline at
the Diamond Light source, and has been supplied in the SIF
format used by `CUTEst <https://github.com/ralna/CUTEst>`_.the data.

These problems have either 66 or 99 unknown parameters, and fit around 5,000 data points.

.. warning::
   |CUTEstWarning|

   
MultiFit Data (Mantid)
----------------------

The folder `examples/benchmark_problems/MultiFit` contains data
for testing the MultFit functionality of Mantid.  This contains
a simple data set, on which two fits are done, and a calibration
dataset from the `MuSR <https://www.isis.stfc.ac.uk/Pages/musr.aspx>`_
spectrometer at ISIS, on which there are four fits available.
See :ref:`The MultiFit documentation<multifit>` for more details.

.. warning::   
   |MantidWarning|
   
   This will also only work using the :ref:`Mantid Minimizers<MantidMinimizers>`.


Muon Data (Mantid)
------------------

In the folder `examples/benchmark_problems/Muon` you will find
data from Muon spectrometers.  The data supplied comes
from the `HiFi <https://www.isis.stfc.ac.uk/Pages/hifi.aspx>`_ and 
`EMU <https://www.isis.stfc.ac.uk/Pages/EMU.aspx>`_ instruments at
STFC's ISIS Neutron and Muon source, and has been supplied in the
format that `Mantid <https://mantidproject.org/>`__ uses to process
the data.

These problems have between 5 and 13 unknown parameters, and fit around 1,000 data points.

.. warning::   
   |MantidWarning|


NIST
----

In the folder `examples/benchmark_problems/NIST` you will find
data from the `NIST Nonlinear Regression <https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`_ test set.

These problems are split into low, average and high difficulty.
They have between 2 and 9 unknown parameters, and
fit between 6 and 250 data points.


Neutron Data (Mantid)
---------------------

In the folder `examples/benchmark_problems/Neutron` you will find
data from Neutron scattering experiments.  The data supplied comes
from the `Engin-X <https://www.isis.stfc.ac.uk/Pages/Engin-X.aspx>`_,
`GEM <https://www.isis.stfc.ac.uk/Pages/gem.aspx>`_,
`eVS <https://www.isis.stfc.ac.uk/Pages/Vesuvio.aspx>`_, and
`WISH <https://www.isis.stfc.ac.uk/Pages/wish.aspx>`_ instruments at
STFC's ISIS Neutron and Muon source, and has been supplied in the
format that `Mantid <https://mantidproject.org/>`__ uses to process
the data.

The size of these problems differ massively per problem.
The Engin-X calibration problems find 7 unknown parameters, and fit to
56-67 data points.
The Engin-X vanadium problems find 4 unknown parameters, and fit to around 14,168
data points.
The eVS problems find 8 unknown parameters, and fit to 1025 data points.
The GEM problem finds 105 unknown parameters, and fits to 1314 data points.
The WISH problems find 30 unknown parameters, and fit to 5 data points.

.. warning::   
   |MantidWarning|


Small Angle Scattering (SASView)
--------------------------------

In the folder `examples/benchmark_problems/SAS_modelling/1D` are
two data sets from small angle scattering experiments.
These are from fitting data to a
`cylinder <http://www.sasview.org/docs/user/models/cylinder.html>`_,
and have been supplied in the format that `SASView <http://www.sasview.org>`__
uses to process the data.

These have 6 unknown parameters, and fit to either 20 or 54 data points.

CUTEst (SIF files)
------------------

The folder `examples/benchmark_problems/SIF` contains
`SIF files <https://github.com/ralna/SIFDecode>`_
encoding least squares problems 
from the `CUTEst <https://github.com/ralna/CUTEst>`_
continuous optimization testing environment.

These are from a wide range of applications.  They have between
2 and 9 unknown parameters, and for the most part fit between
6 and 250 data points, although the `VESUVIO*` examples (from
the `VESUVIO <https://www.isis.stfc.ac.uk/Pages/Vesuvio.aspx>`_
instrument at ISIS) have 1025 data points (with 8 unknown parameters).

.. warning::
   |CUTEstWarning|


Simple tests
------------

The folder `examples/benchmark_problems/simple_tests` contains
a number of simple tests with known, and easy to obtain,
answers.  We recommend that this is used to test any new data sets
that are added, and also that any new parsers reimplement these
data sets and models (if possible).


.. |CUTEstWarning| replace::
		   The external packages CUTEst and pycutest must be installed to run
		   this data set.   At present, this is only available for linux systems.
		   See :ref:`CUTEst` for details.

.. |MantidWarning| replace::
		   The external package Mantid must be installed to run
		   this data set.  See :ref:`InstallMantid` for details.
