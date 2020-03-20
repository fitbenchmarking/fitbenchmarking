.. _how:

##############################
How does FitBenchmarking work?
##############################

FitBenchmarking takes data and models from real world applications
and data analysis packages, and fits them using a range of
fitting software.

.. figure:: ../../images/FitBenchmarkingConcept.png  
   :alt: FitBenchmarking Concept
   :width: 100.0%

:ref:`Minimizers` contains the fitting software that Fitbenchmarking currently supports,
and we've made it straightforward to test against new software by
following the instructions in :ref:`controllers` -- the software just needs
to be callable from  python.


:ref:`BenchmarkProblems` gives the current list of data analysis software we support, 
and again we've made it possible to extend this list by following the steps in 
:ref:`controllers`.

Once you have chosen which minimizers you want to compare on which problems,
running FitBenchmarking will give you a comparison.
:ref:`BenchmarkingParadigm` describes what we compare, and how we do
the comparisons.


.. _Minimizers:

**********
Minimizers
**********

In alphabetical order:

Bumps
-----
`Bumps <https://bumps.readthedocs.io>`_ is a set of data fitting (and Bayesian uncertainty analysis) routines.
It came out of the University of Maryland and NIST as part of the DANSE
(*Distributed Data Analysis of Neutron Scattering Experiments*) project.

FitBenchmarking currently supports the Bumps minimizers:

* `Nelder-Mead Simplex <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#nelder-mead-simplex>`_ (:code:`amoeba`)
  
* `Levenberg-Marquardt <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#fit-lm>`_  (:code:`lm`)
  
* `Quasi-Newton BFGS <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#quasi-newton-bfgs>`_ (:code:`newton`)
  
* `Differential Evolution <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#differential-evolution>`_ (:code:`de`)
  
* `MINPACK <https://github.com/bumps/bumps/blob/96b5100fc3d5b9485bd4a444c83a33617b74aa9d/bumps/mpfit.py>`_ (:code:`mp`)  This is a translation of `MINPACK` to Python.

**Links** `GitHub - bumps <https://github.com/bumps/bumps>`_
  
DFO
---

There are two Deriviate-Free Optimization packages, `DFO-LS <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ and
`DFO-GN <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_.
They are derivative free optimization solvers that were developed by Lindon Roberts at the University
of Oxford, in conjunction with NAG.  They are particularly well suited for solving noisy problems.

FitBenchmarking currently supports the DFO minimizers:

* `Derivative-Free Optimizer for Least Squares <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ (:code:`dfols`)
  
* `Derivative-Free Gauss-Newton Solver <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ (:code:`dfogn`)

 **Links** `GitHub - DFO-GN <https://github.com/numericalalgorithmsgroup/dfogn>`_ `GitHub - DFO-LS <https://github.com/numericalalgorithmsgroup/dfols>`_

GSL
---

The `GNU Scientific Library <https://www.gnu.org/software/gsl/>`_ is a numerical library that
provides a wide range of mathematical routines.  We call GSL using  the `pyGSL Python interface
<https://sourceforge.net/projects/pygsl/>`_.

The GSL routines have a number of parameters that need to be chosen, often without default suggestions.
We have taken the values as used by Mantid. 

We provide implementations for the following
packages in the `multiminimize <https://www.gnu.org/software/gsl/doc/html/multimin.html>`_ and `multifit <https://www.gnu.org/software/gsl/doc/html/nls.html>`_ sections of the library:


* `Levenberg-Marquardt (unscaled) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multifit_nlin.lmder>`_ (:code:`lmder`)

* `Levenberg-Marquardt (scaled) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multifit_nlin.lmsder>`_ (:code:`lmsder`)
  
* `Nelder-Mead Simplex Algorithm <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.nmsimplex>`_ (:code:`nmsimplex`)

* `Nelder-Mead Simplex Algorithm (version 2) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.nmsimplex2>`_ (:code:`nmsimplex2`)
  
* `Polak-Ribiere Conjugate Gradient Algorithm <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.conjugate_pr>`_ (:code:`conjugate_pr`)
  
* `Fletcher-Reeves Conjugate-Gradient <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.conjugate_fr>`_ (:code:`conjugate_fr`)
  
* `The vector quasi-Newton BFGS method <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.vector_bfgs>`_ (:code:`vector_bfgs`)
  
* `The vector quasi-Newton BFGS method (version 2) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.vector_bfgs2>`_ (:code:`vector_bfgs2`)
  
* `Steepest Descent <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.steepest_descent>`_ (:code:`steepest_descent`)

**Links** `SourceForge PyGSL <http://pygsl.sourceforge.net/>`_

Mantid
------

`Mantid <https://www.mantidproject.org>` is a framework created to
manipulate and analyse neutron scattering and muon spectroscopy data.
It has support for a number of minimizers, most of which are from GSL.

* `BFGS <https://docs.mantidproject.org/nightly/fitting/fitminimizers/BFGS.html>`_ (:code:`BFGS`)
  
* `Conjugate gradient (Fletcher-Reeves) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/FletcherReeves.html>`_ (:code:`Conjugate gradient (Fletcher-Reeves imp.)`)

* `Conjugate gradient (Polak-Ribiere) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/PolakRibiere.html>`_ (:code:`Conjugate gradient (Polak-Ribiere imp.)`)

* `Damped GaussNewton <https://docs.mantidproject.org/nightly/fitting/fitminimizers/DampedGaussNewton.html>`_ (:code:`Damped GaussNewton`)

* `Levenberg-Marquardt algorithm <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardt.html>`_ (:code:`Levenberg-Marquardt`)
  
* `Levenberg-Marquardt MD <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardtMD.html>`_ (:code:`Levenberg-MarquardtMD`) - An implementation of Levenberg-Marquardt intended for MD workspaces, where work is divided into chunks to acheive a greater efficiency for a large number of data points.

* `Simplex <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`_ (:code:`simplex`)

* `SteepestDescent <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`_ (:code:`SteepestDescent`)
  
* `Trust Region <https://docs.mantidproject.org/nightly/fitting/fitminimizers/TrustRegion.html>`_ (:code:`Trust Region`) - An implementation of one of the algorithms available in RALFit.

 **Links** `GitHub - Mantid <https://github.com/mantidproject/mantid>`_ `Mantid's Fitting Docs <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html>`_


Minuit
------

CERN developed the `Minuit <http://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/>`_ package to find the minimum value of a multi-parameter function, and also to compute the uncertainties.
We interface via the python interface `iminuit <https://iminuit.readthedocs.io>`_

* `Minuit's MIGRAD <https://root.cern.ch/root/htmldoc/guides/minuit2/Minuit2.pdf>`_ (:code:`minuit`)

**Links** `Github - iminuit <https://github.com/scikit-hep/iminuit>`_

RALFit
------

`RALFit <https://ralfit.readthedocs.io/projects/Fortran/en/latest/>`_
is a nonlinear least-squares solver, the development of which was funded
by the EPSRC grant `Least-Squares: Fit for the Future`.  RALFit is designed to be able
to take advantage of higher order derivatives, although only first
order derivatives are currently utilized in FitBenchmarking.

* Gauss-Newton, trust region method (:code:`gn`)
* Hybrid Newton/Gauss-Newton, trust region method (:code:`hybrid`)
* Gauss-Newton, regularization (:code:`gn_reg`)
* Hybrid Newton/Gauss-Newton, regularization (:code:`hybrid_reg`)

**Links** `Github - RALFit <https://github.com/ralna/ralfit/>`_. RALFit's Documentation on: `Gauss-Newton/Hybrid models <https://ralfit.readthedocs.io/projects/Fortran/en/latest/method.html#the-models>`_,  `the trust region method <https://ralfit.readthedocs.io/projects/Fortran/en/latest/method.html#the-trust-region-method>`_ and  `The regularization method <https://ralfit.readthedocs.io/projects/C/en/latest/method.html#regularization>`_

SciPy
-----

`SciPy <https://www.scipy.org>`_ is the standard python package for mathematical
software.  In particular, we use the `least_squares <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html#scipy.optimize.least_squares>`_
solver from the optimization chapter the SciPy's library.

* Levenberg-Marquardt with supplied Jacobian (:code:`lm-scipy`)  - a wrapper around MINPACK
* Levenberg-Marquardt with no Jacobian passed (:code:`lm-scipy-no-jac`)  - as above, but using MINPACK's approximate Jacobian
* The Trust Region Reflective algorithm (:code:`trf`)
* A dogleg algorithm with rectangular trust regions (:code:`dogbox`)

**Links** `Github - SciPy least_squares <https://github.com/scipy/scipy/blob/master/scipy/optimize/_lsq/least_squares.py>`_


.. _BenchmarkProblems:

******************   
Benchmark problems
******************

To help choose between the different minmizers above, FitBenchmarking
comes with some curated Benchmark problems—although it’s straightforward
add custom data sets to the benchmark, if that is more appropriate. We
have included some standard nonlinear least-squares test problems in the
form of the `NIST nonlinear regression set <https://www.itl.nist.gov/div898/strd/nls/nls_main.shtml>`_
and the relevant problems from the `CUTEst problem set <https://github.com/ralna/CUTEst/wiki>`_,
together with some real-world 
data sets that have been extracted from `Mantid <https://www.mantidproject.org>`_ and
`SASView <https://www.sasview.org>`_ usage examples and system tests.

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
suite to encompass new categories. The Fitbenchmarking framework has
been designed to make it easy to integrate new problem sets, and a any
new problem set added to the framework can be tested with any and all of
the available fitting methods.

.. _BenchmarkingParadigm:

*************************
The Benchmarking Paradigm
*************************

