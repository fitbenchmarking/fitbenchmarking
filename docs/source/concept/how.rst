.. _how:

##############################
How does FitBenchmarking work?
##############################

Place holder for how FitBenchmarking is used.
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

**Links** `GitHub <https://github.com/bumps/bumps>`_
  
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

* `Levenberg-Marquardt <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multifit_nlin.lmsder>`_ (:code:`lmsder`)
  
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

* `BFGS <https://docs.mantidproject.org/nightly/fitting/fitminimizers/BFGS.html>`_ (:code:`BFGS`)
  
* `Conjugate gradient (Fletcher-Reeves) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/FletcherReeves.html>`_ (:code:`Conjugate gradient (Fletcher-Reeves imp.)`)

* `Conjugate gradient (Polak-Ribiere) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/PolakRibiere.html>`_ (:code:`Conjugate gradient (Polak-Ribiere imp.)`)

* `Damped GaussNewton <https://docs.mantidproject.org/nightly/fitting/fitminimizers/DampedGaussNewton.html>`_ (:code:`Damped GaussNewton`)

* `Levenberg-Marquardt <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardt.html>`_ (:code:`Levenberg-Marquardt`)
  
* `Levenberg-Marquardt MD <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardtMD.html>`_ (:code:`Levenberg-MarquardtMD`) - An implementation of Levenberg-Marquardt intended for MD workspaces, where work is divided into chunks to acheive a greater efficiency for a large number of data points.

* `Simplex <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`_ (:code:`simplex`)

* `SteepestDescent <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`_ (:code:`SteepestDescent`)
  
* `Trust Region <https://docs.mantidproject.org/nightly/fitting/fitminimizers/TrustRegion.html>`_ (:code:`Trust Region`)


Minuit
------




RALFit
------




SciPy
-----





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

Each of the test problems contain: a data set consisting of points
:math:`(x_i, y_i)` (with optional errors on :math:`y_i`,
:math:`\sigma_i`), a definition of the fitting function,
:math:`f({\boldsymbol{\beta}};x)`, (at least) one set of initial values
for the function parameters :math:`{\boldsymbol{\beta}}_0`, and an
optional set of target values that the parameters are expected to reach,
:math:`{\boldsymbol{\beta}}_*`. If a problem doesn’t have observational
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
