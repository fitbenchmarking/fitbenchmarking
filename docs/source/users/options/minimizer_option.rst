.. _minimizer_option:

===================
 Minimizer Options
===================

This section is used to declare the minimizers to use for each fitting
software. If a fitting software has been selected in :ref:`fitting_option`
then a default set of minimizers for that solver will be run unless alternative
minimizer options have been set. All minimizers for a software are included on
the default list of minimizers unless otherwise stated.

.. warning::

   Options set in this section will only have an effect if the related
   software is also set in :ref:`fitting_option` (either explicitly, or
   as a default option).

.. _bumps:

Bumps (:code:`bumps`)
=====================

`Bumps <https://bumps.readthedocs.io>`__ is a set of data fitting (and Bayesian uncertainty analysis) routines.
It came out of the University of Maryland and NIST as part of the DANSE
(*Distributed Data Analysis of Neutron Scattering Experiments*) project.

FitBenchmarking currently supports the Bumps minimizers:

* `Nelder-Mead Simplex <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#nelder-mead-simplex>`__ (:code:`amoeba`)

* `Levenberg-Marquardt <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#fit-lm>`__  (:code:`lm-bumps`) This is `mpfit`, a translation of `MINPACK` to Python.

* `Quasi-Newton BFGS <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#quasi-newton-bfgs>`__ (:code:`newton`)

* `Differential Evolution <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#differential-evolution>`__ (:code:`de`)

* `scipy's leastsq <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#fit-lm>`__ (:code:`scipy-leastsq`)  This calls scipy's Levenberg-Marquardt method. Note that this was the default method for `lm` prior to Bumps v0.8.2.

* `DiffeRential Evolution Adaptive Metropolis <https://bumps.readthedocs.io/en/latest/guide/optimizer.html#dream>`__ (:code:`dream`)

**Licence** The main licence file for Bumps is `here <https://github.com/bumps/bumps/blob/master/LICENSE.txt>`__.  Individual files have their own copyright and licence
-- if you plan to incorporate this in your own software you should first check that the
licences used are compatible.

**Links** `GitHub - bumps <https://github.com/bumps/bumps>`__

The Bumps minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    bumps: amoeba
           lm-bumps
           newton
           de
           scipy-leastsq
           dream

.. warning::
   The additional dependency Bumps must be installed for this to be available;
   See :ref:`extra_dependencies`.

.. note::
   `de` is not included in the default list of minimizers for bumps. To run this solver, you must
   explicitly set the minimizer as seen above.

.. _ceres:

Ceres Solver (``ceres``)
=============


`Ceres Solver <http://ceres-solver.org/>`__ is an open source C++ library for modeling and solving large, complicated optimization problems. 
It can be used to solve Non-linear Least Squares problems with bounds constraints and general unconstrained optimization problems.

FitBenchmarking currently supports the Ceres Solver minimizers:

* `Levenberg-Marquardt <http://ceres-solver.org/nnls_solving.html#levenberg-marquardt>`__ (:code:`Levenberg-Marquardt`)
* `Dogleg <http://ceres-solver.org/nnls_solving.html#dogleg>`__ (:code:`Dogleg`)
* `Steepest Descent <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`steepest_descent`)
* `BFGS algorithm <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`BFGS`)
* `LBFGS algorithm <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`LBFGS`)
* `Fletcher-Reeves Non Linear Conjugate-Gradient <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`Fletcher_Reeves`)
* `Polak-Ribiere Non Linear Conjugate-Gradient <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`Polak_Ribiere`)
* `Hestenes-Stiefel Non Linear Conjugate-Gradient <http://ceres-solver.org/nnls_solving.html#line-search-methods>`__ (:code:`Hestenes_Stiefel`)

**Licence** Ceres Solver is available under the new BSD licence -- details can be found `here <http://ceres-solver.org/license.html>`__ 

**Links** `Ceres Solver <http://ceres-solver.org/>`__ `PyCeres - Ceres Python Bindings <https://github.com/Edwinem/ceres_python_bindings>`__

The Ceres Solver minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    ceres: Levenberg_Marquardt
           Dogleg
           BFGS
           LBFGS
           steepest_descent
           Fletcher_Reeves
           Polak_Ribiere
           Hestenes_Stiefel


.. warning::
   The additional dependency Ceres Solver must be installed for this to be available;
   See :ref:`extra_dependencies`.

.. note::
   The PyCeres currently only works with Ceres Solver versions 2.0.0 

.. _dfo:

DFO (``dfo``)
=============

`DFO-LS <https://numericalalgorithmsgroup.github.io/dfols/build/html/index.html>`__ is a 
derivative free optimization solver developed by Lindon Roberts at the University
of Oxford, in conjunction with NAG.  It is particularly well suited for solving noisy problems.

FitBenchmarking currently supports the DFO minimizer:

* `Derivative-Free Optimizer for Least Squares <https://numericalalgorithmsgroup.github.io/dfols/build/html/index.html>`__ (:code:`dfols`)

**Licence** `DFO-LS <https://github.com/numericalalgorithmsgroup/dfols/blob/master/LICENSE.txt>`__ is available under the GPL-3 licence. A proprietary licence is also available from `NAG <https://nag.com/worldwide-contact-information/>`__ .

**Links** `GitHub - DFO-LS <https://github.com/numericalalgorithmsgroup/dfols>`__

The DFO minimizer is set as follows:

.. code-block:: rst

    [MINIMIZERS]
    dfo: dfols

.. warning::
   Additional dependencies `DFO-LS` must be installed for
   these to be available;
   See :ref:`extra_dependencies`.

.. _gofit:

GOFit (``gofit``)
=================

`GOFit <https://github.com/ralna/GOFit>`__ is a package of C++ algorithms with Python interfaces designed
for the global optimization of parameters in curve fitting, i.e. for nonlinear least-squares problems
arising from curve fitting. It is also included with Mantid since release 6.5.

FitBenchmarking currently supports the GOFit minimizers:

*  Multistart Global Minimizer (:code:`multistart`)

*  Alternating Multistart Global Minimizer (:code:`alternating`)

*  Quadratic Regularisation Local Minimizer (:code:`regularisation`)

**Links** `Documentation <https://ralna.github.io/GOFit/>`__

**Licence** GOFit is available under a `3-clause BSD Licence <https://github.com/ralna/GOFit/blob/master/LICENSE>`__

The GOFit minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    gofit: multistart
           alternating
           regularisation

.. note::
   The alternating minimizer currently only supports Crystal Field problems.

.. warning::
   The additional dependency GOFit must be installed to use these minimizers. See :ref:`extra_dependencies`.

.. _gradient-free:

Gradient-Free-Optimizers (``gradient_free``)
============================================

`Gradient-Free-Optimizers <https://github.com/SimonBlanke/Gradient-Free-Optimizers>`__ are a collection of
gradient-free methods capable of solving various optimization problems. Please note that Gradient-Free-Optimizers
must be run with problems that have finite bounds on all parameters.

*  Hill Climbing (:code:`HillClimbingOptimizer`)

*  Repulsing Hill Climbing (:code:`RepulsingHillClimbingOptimizer`)

*  Simulated Annealing (:code:`SimulatedAnnealingOptimizer`)

*  Random Search (:code:`RandomSearchOptimizer`)

*  Random Restart Hill Climbing (:code:`RandomRestartHillClimbingOptimizer`)

*  Random Annealing (:code:`RandomAnnealingOptimizer`)

*  Parallel Tempering (:code:`ParallelTemperingOptimizer`)

*  Particle Swarm (:code:`ParticleSwarmOptimizer`)

*  Evolution Strategy (:code:`EvolutionStrategyOptimizer`)

*  Bayesian (:code:`BayesianOptimizer`)

*  Tree Structured Parzen Estimators (:code:`TreeStructuredParzenEstimators`)

*  Decision Tree (:code:`DecisionTreeOptimizer`)

**Licence** The Gradient-Free-Optimizers package is available under an `MIT Licence <https://github.com/SimonBlanke/Gradient-Free-Optimizers/blob/master/LICENSE>`__ .


The `gradient_free` minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    gradient_free: HillClimbingOptimizer
                   RepulsingHillClimbingOptimizer
                   SimulatedAnnealingOptimizer
                   RandomSearchOptimizer
                   RandomRestartHillClimbingOptimizer
                   RandomAnnealingOptimizer
                   ParallelTemperingOptimizer
                   ParticleSwarmOptimizer
                   EvolutionStrategyOptimizer
                   BayesianOptimizer
                   TreeStructuredParzenEstimators
                   DecisionTreeOptimizer

.. warning::
   The additional dependency Gradient-Free-Optimizers must be installed for this to be available;
   See :ref:`extra_dependencies`.

.. note::
   BayesianOptimizer, TreeStructuredParzenEstimators and DecisionTreeOptimizer may be slow running and
   so are not run by default when `gradient_free` software is selected. To run these minimizers you must
   explicity set them as seen above.

.. _gsl:

GSL (``gsl``)
=============

The `GNU Scientific Library <https://www.gnu.org/software/gsl/>`__ is a numerical library that
provides a wide range of mathematical routines.  We call GSL using  the `pyGSL Python interface
<https://sourceforge.net/projects/pygsl/>`__.

The GSL routines have a number of parameters that need to be chosen, often without default suggestions.
We have taken the values as used by Mantid.

We provide implementations for the following
packages in the `multiminimize <https://www.gnu.org/software/gsl/doc/html/multimin.html>`__ and `multifit <https://www.gnu.org/software/gsl/doc/html/nls.html>`__ sections of the library:


* `Levenberg-Marquardt (unscaled) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multifit__nlin.lmder>`__ (:code:`lmder`)

* `Levenberg-Marquardt (scaled) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multifit_nlin.lmsder>`__ (:code:`lmsder`)

* `Nelder-Mead Simplex Algorithm <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.nmsimplex>`__ (:code:`nmsimplex`)

* `Nelder-Mead Simplex Algorithm (version 2) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.nmsimplex2>`__ (:code:`nmsimplex2`)

* `Polak-Ribiere Conjugate Gradient Algorithm <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.conjugate_pr>`__ (:code:`conjugate_pr`)

* `Fletcher-Reeves Conjugate-Gradient <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.conjugate_fr>`__ (:code:`conjugate_fr`)

* `The vector quasi-Newton BFGS method <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.vector_bfgs>`__ (:code:`vector_bfgs`)

* `The vector quasi-Newton BFGS method (version 2) <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.vector_bfgs2>`__ (:code:`vector_bfgs2`)

* `Steepest Descent <http://pygsl.sourceforge.net/api/pygsl.html#pygsl.multiminimize.steepest_descent>`__ (:code:`steepest_descent`)

**Links** `SourceForge PyGSL <http://pygsl.sourceforge.net/>`__

**Licence** The GNU Scientific Library is available under the `GPL-3 licence <https://www.gnu.org/licenses/gpl-3.0.html>`__ .

The GSL minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    gsl: lmsder
         lmder
         nmsimplex
         nmsimplex2
         conjugate_pr
         conjugate_fr
         vector_bfgs
         vector_bfgs2
         steepest_descent

.. warning::
   The external packages GSL and pygsl must be installed to use these minimizers.

.. _horace:

Horace (``horace``)
===================

`Horace <https://pace-neutrons.github.io/Horace/>`_ is described as *a suite of programs for
the visiualization and analysis from time-of-flight neutron inelastic scattering
spectrometers.*  We currently support:

* Levenberg-Marquardt (:code:`lm-lsqr`)

**Licence** Matlab must be installed to use Horace within FitBenchmarking, which is a
`proprietary product <https://www.mathworks.com/pricing-licensing.html>`__.
Horace is made available under the the `GPL-3 licence <https://www.gnu.org/licenses/gpl-3.0.html>`__.

.. code-block:: rst

    [MINIMIZERS]
    horace: lm-lsqr


.. note:: 
   If you have a non standard installation of Horace please set the `HORACE_LOCATION` (e.g on IDAaaS). 

.. warning::
   The Horace Toolbox and MATLAB must be installed for this to be available; see :ref:`external-instructions`.


.. _mantid:

Mantid (``mantid``)
===================

`Mantid <https://www.mantidproject.org>`__ is a framework created to
manipulate and analyze neutron scattering and muon spectroscopy data.
It has support for a number of minimizers, most of which are from GSL.

* `BFGS <https://docs.mantidproject.org/nightly/fitting/fitminimizers/BFGS.html>`__ (:code:`BFGS`)

* `Conjugate gradient (Fletcher-Reeves) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/FletcherReeves.html>`__ (:code:`Conjugate gradient (Fletcher-Reeves imp.)`)

* `Conjugate gradient (Polak-Ribiere) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/PolakRibiere.html>`__ (:code:`Conjugate gradient (Polak-Ribiere imp.)`)

* `Damped GaussNewton <https://docs.mantidproject.org/nightly/fitting/fitminimizers/DampedGaussNewton.html>`__ (:code:`Damped GaussNewton`)

* `FABADA <https://docs.mantidproject.org/nightly/concepts/FABADA.html>`__ (:code:`FABADA`)

* `Levenberg-Marquardt algorithm <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardt.html>`__ (:code:`Levenberg-Marquardt`)

* `Levenberg-Marquardt MD <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardtMD.html>`__ (:code:`Levenberg-MarquardtMD`) - An implementation of Levenberg-Marquardt intended for MD workspaces, where work is divided into chunks to achieve a greater efficiency for a large number of data points.

* `Simplex <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`__ (:code:`Simplex`)

* `SteepestDescent <https://docs.mantidproject.org/nightly/fitting/fitminimizers/GradientDescent.html>`__ (:code:`SteepestDescent`)

* `Trust Region <https://docs.mantidproject.org/nightly/fitting/fitminimizers/TrustRegion.html>`__ (:code:`Trust Region`) - An implementation of one of the algorithms available in RALFit.

 **Links** `GitHub - Mantid <https://github.com/mantidproject/mantid>`__ `Mantid's Fitting Docs <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html>`__

**Licence** Mantid is available under the `GPL-3 licence <https://github.com/mantidproject/mantid/blob/master/LICENSE.txt>`__ .


The Mantid minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    mantid: BFGS
            Conjugate gradient (Fletcher-Reeves imp.)
            Conjugate gradient (Polak-Ribiere imp.)
            Damped GaussNewton
	    FABADA
            Levenberg-Marquardt
            Levenberg-MarquardtMD
            Simplex
            SteepestDescent
            Trust Region

.. warning::
   The external package Mantid must be installed to use these minimizers.

.. _levmar:

Levmar (``levmar``)
===================

The `levmar <http://users.ics.forth.gr/~lourakis/levmar/>`__ package
which implements the Levenberg-Marquardt method for nonlinear least-squares.
We interface via the python interface `available on PyPI <https://pypi.org/project/levmar/>`__.

* Levenberg-Marquardt with supplied Jacobian (:code:`levmar`)  - the Levenberg-Marquardt method

**Licence** Levmar is available under the `GPL-3 licence <http://www.gnu.org/copyleft/gpl.html>`__ .  A paid licence for proprietary commerical use is `available from the author <http://users.ics.forth.gr/~lourakis/levmar/faq.html#Q37>`__ .

The `levmar` minimizer is set as follows:

.. code-block:: rst

   [MINIMIZERS]
   levmar: levmar


.. warning::
   The additional dependency levmar must be installed for this to be available;
   See :ref:`extra_dependencies`. This package also requires the BLAS and LAPACK
   libraries to be present on the system.


.. _lmfit:

LMFIT (``lmfit``)
===================

The `lmfit <https://lmfit.github.io/lmfit-py/index.html>`__ package provides simple tools to help you build complex fitting models 
for non-linear least-squares problems and apply these models to real data. Lmfit provides a high-level interface to non-linear 
optimization and curve fitting problems for Python. It builds on and extends many of the optimization methods of 
`scipy.optimize <https://docs.scipy.org/doc/scipy/reference/optimize.html>`__.

* Levenberg-Marquardt (:code:`leastsq`)
* Least-Squares minimization, using Trust Region Reflective method (:code:`least_squares`)
* Differential evolution (:code:`differential_evolution`)
* Adaptive Memory Programming for Global Optimization (:code:`ampgo`)
* Nelder-Mead (:code:`nelder`)
* L-BFGS-B (:code:`lbfgsb`)
* Powell (:code:`powell`)
* Conjugate-Gradient (:code:`cg`)
* Newton-CG (:code:`newton`)
* Cobyla (:code:`cobyla`)
* BFGS (:code:`bfgs`)
* Truncated Newton (:code:`tnc`)
* Newton-CG trust-region (:code:`trust-ncg`)
* Nearly exact trust-region (:code:`trust-exact`)
* Newton GLTR trust-region (:code:`trust-krylov`)
* Trust-region for constrained optimization (:code:`trust-constr`)
* Dog-leg trust-region (:code:`dogleg`)
* Sequential Linear Squares Programming (:code:`slsqp`)
* `Maximum likelihood via Monte-Carlo Markov Chain <https://emcee.readthedocs.io/en/stable/>`__ (:code:`emcee`)
* Simplicial Homology Global Optimization (:code:`shgo`)
* Dual Annealing optimization (:code:`dual_annealing`)

**Licence** LMFIT is available the new BSD-3 licence -- details can be found `here <https://lmfit.github.io/lmfit-py/installation.html#copyright-licensing-and-re-distribution>`__

The `lmfit` minimizer is set as follows:

.. code-block:: rst

   [MINIMIZERS]
   lmfit: differential_evolution
          powell
          cobyla
          slsqp
          emcee
          nelder
          least_squares
          trust-ncg
          trust-exact
          trust-krylov
          trust-constr
          dogleg
          leastsq
          newton
          tnc
          lbfgsb
          bfgs
          cg
          ampgo
          shgo
          dual_annealing
.. note::
   The shgo solver is particularly slow running and should generally be avoided. As a result, this solver is
   not run by default when `lmfit` software is selected. In order to run this minimizer, you must explicitly
   set it as above.

.. warning::
   emcee uses a Markov Chain Monte Carlo package and assumes that the prior is Uniform. This may not perform well for certain fitting problems.

.. _matlab:

Matlab (``matlab``)
===================

We call the `fminsearch <https://uk.mathworks.com/help/matlab/ref/fminsearch.html>`__
function from `MATLAB <https://uk.mathworks.com/products/matlab.html>`__, using the
MATLAB Engine API for Python.

* Nelder-Mead Simplex (:code:`Nelder-Mead Simplex`)

**Licence** Matlab is a `proprietary product <https://www.mathworks.com/pricing-licensing.html>`__ .

The `matlab` minimizer is set as follows:

.. code-block:: rst

   [MINIMIZERS]
   matlab: Nelder-Mead Simplex

.. warning::
   MATLAB must be installed for this to be available; See :ref:`external-instructions`.

.. _matlab-curve:

Matlab Curve Fitting Toolbox (``matlab_curve``)
===============================================

We call the `fit <https://uk.mathworks.com/help/curvefit/fit.html>`_
function from the `MATLAB Curve Fitting Toolbox <https://uk.mathworks.com/help/curvefit/index.html>`_,
using the MATLAB Engine API for Python.

* Levenberg-Marquardt (:code:`Levenberg-Marquardt`)
* Trust-Region (:code:`Trust-Region`)

**Licence** Matlab and the Curve Fitting Toolbox are both `proprietary products <https://www.mathworks.com/pricing-licensing.html>`__ .

The `matlab_curve` minimizers are set as follows:

.. code-block:: rst

   [MINIMIZERS]
   matlab_curve: Levenberg-Marquardt
                 Trust-Region

.. warning::
   MATLAB Curve Fitting Toolbox must be installed for this to be available; See :ref:`external-instructions`.

.. _matlab-opt:

Matlab Optimization Toolbox (``matlab_opt``)
============================================

We call the `lsqcurvefit <https://uk.mathworks.com/help/optim/ug/lsqcurvefit.html>`__
function from the `MATLAB Optimization Toolbox <https://uk.mathworks.com/products/optimization.html>`__,
using the MATLAB Engine API for Python.

* Levenberg-Marquardt (:code:`levenberg-marquardt`)
* Trust-Region-Reflective (:code:`trust-region-reflective`)

**Licence** Matlab and the Optimization Toolbox are both `proprietary products <https://www.mathworks.com/pricing-licensing.html>`__ .

The `matlab_opt` minimizers are set as follows:

.. code-block:: rst

   [MINIMIZERS]
   matlab_opt: levenberg-marquardt
               trust-region-reflective

.. warning::
   MATLAB Optimization Toolbox must be installed for this to be available; See :ref:`external-instructions`.

.. _matlab-stats:

Matlab Statistics Toolbox (``matlab_stats``)
============================================


We call the `nlinfit <https://uk.mathworks.com/help/stats/nlinfit.html>`__
function from the `MATLAB Statistics Toolbox <https://uk.mathworks.com/products/statistics.html>`__,
using the MATLAB Engine API for Python.

* Levenberg-Marquardt (:code:`Levenberg-Marquardt`)

**Licence** Matlab and the Statistics Toolbox are both `proprietary products <https://www.mathworks.com/pricing-licensing.html>`__ .

The `matlab_stats` minimizer is set as follows:

.. code-block:: rst

  [MINIMIZERS]
  matlab_stats: Levenberg-Marquardt

.. warning::
   MATLAB Statistics Toolbox must be installed for this to be available; See :ref:`external-instructions`.

.. _minuit:

Minuit (``minuit``)
===================

CERN developed the `Minuit 2 <https://root.cern.ch/doc/master/Minuit2Page.html>`__ package
to find the minimum value of a multi-parameter function, and also to compute the
uncertainties.
We interface via the python interface `iminuit <https://iminuit.readthedocs.io>`__ with
support for the 2.x series.

* `Minuit's MIGRAD <https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.migrad>`__ (:code:`migrad`)
* `Minuit's SIMPLEX <https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.simplex>`__ (:code:`simplex`)

**Links** `Github - iminuit <https://github.com/scikit-hep/iminuit>`__

**Licence** iminuit is released under the `MIT licence <https://github.com/scikit-hep/iminuit/blob/develop/LICENSE>`__, while Minuit 2 is `LGPL v2 <https://github.com/root-project/root/blob/master/LICENSE>`__ .

The Minuit minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    minuit: migrad
            simplex

.. warning::
   The additional dependency Minuit must be installed for this to be available;
   See :ref:`extra_dependencies`.

.. _nlopt:

NLopt (``nlopt``)
===================

`NLopt <https://nlopt.readthedocs.io/en/latest/>`__ is a free/open-source library for nonlinear optimization, providing a
common interface for a number of different free optimization routines available
online as well as original implementations of various other algorithms

* Bound Optimization BY Quadratic Approximation (:code:`LN_BOBYQA`)
* NEW Unconstrained Optimization Algorithm (:code:`LN_NEWUOA`)
* NEW Unconstrained Optimization Algorithm, bound algorithm (:code:`LN_NEWUOA_BOUND`)
* Principal-axis method (:code:`LN_PRAXIS`)
* Sequential Least Squares Programming (:code:`LD_SLSQP`)
* Shifted limited-memory variable-metric (rank 1) (:code:`LD_VAR1`)
* Shifted limited-memory variable-metric (rank 2) (:code:`LD_VAR2`)
* Augmented Lagrangian local (:code:`AUGLAG`)
* Augmented Lagrangian local (equality constraints) (:code:`AUGLAG_EQ`)
* Nelder-Mead Simplex (:code:`LN_NELDERMEAD`)
* Subplex (:code:`LN_SBPLX`)
* Constrained Optimization BY Linear Approximations (:code:`LN_COBYLA`)
* Conservative convex separable approximation (:code:`LD_CCSAQ`)
* Method of Moving Asymptotes (:code:`LD_MMA`)
* Newton (:code:`LD_TNEWTON`)
* Newton preconditioned by the low-storage BFGS algorithm (:code:`LD_TNEWTON_PRECOND`)
* Newton with steepest-descent restarting (:code:`LD_TNEWTON_RESTART`)
* Newton preconditioned by the low-storage BFGS algorithm with steepest-descent restarting (:code:`LD_TNEWTON_PRECOND_RESTART`)
* LBFGS, and derivative-free algorithm (:code:`LD_LBFGS`)
* DIviding RECTangles (:code:`GN_DIRECT`)
* DIviding RECTangles (locally biased) (:code:`GN_DIRECT_L`)
* DIviding RECTangles (locally biased which uses some randomization) (:code:`GN_DIRECT_L_RAND`)
* DIviding RECTangles (unscaled variant) (:code:`GNL_DIRECT_NOSCAL`)
* DIviding RECTangles (locally biased and unscaled variant) (:code:`GN_DIRECT_L_NOSCAL`)
* DIviding RECTangles (locally biased, unscaled variant which uses some randomization) (:code:`GN_DIRECT_L_RAND_NOSCAL`)
* DIviding RECTangles (based on the original Fortran code by Gablonsky et al. (1998-2001)) (:code:`GN_ORIG_DIRECT`)
* DIviding RECTangles (based on the original Fortran code by Gablonsky et al. (1998-2001) and locally biased ) (:code:`GN_ORIG_DIRECT_L`)
* Controlled Random Search (:code:`GN_CRS2_LM`)
* Multi-Level Single-Linkage, low-discrepancy sequence (:code:`G_MLSL_LDS`)
* Multi-Level Single-Linkage (:code:`G_MLSL`)
* Stochastic Global Optimization (:code:`GD_STOGO`)
* Stochastic Global Optimizatiom, randomized variant (:code:`GD_STOGO_RAND`)
* AGS (:code:`GN_AGS`)
* Improved Stochastic Ranking Evolution Strategy (:code:`GN_ISRES`)

The Nlopt minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    nlopt: LN_BOBYQA
           LN_NEWUOA
           LN_NEWUOA_BOUND
           LN_PRAXIS
           LD_SLSQP
           LD_VAR2
           LD_VAR1
           AUGLAG
           AUGLAG_EQ
           LN_NELDERMEAD
           LN_SBPLX
           LN_COBYLA
           LD_CCSAQ
           LD_MMA
           LD_TNEWTON_PRECOND_RESTART
           LD_TNEWTON_PRECOND
           LD_TNEWTON_RESTART
           LD_TNEWTON
           LD_LBFGS
           GN_DIRECT
           GN_DIRECT_L
           GN_DIRECT_L_RAND
           GNL_DIRECT_NOSCAL
           GN_DIRECT_L_NOSCAL
           GN_DIRECT_L_RAND_NOSCAL
           GN_ORIG_DIRECT
           GN_ORIG_DIRECT_L
           GN_CRS2_LM
           G_MLSL_LDS
           G_MLSL
           GD_STOGO
           GD_STOGO_RAND
           GN_AGS
           GN_ISRES

.. note::
   The global optimization solvers are not run by default when `nlopt` software is selected. In order to run these minimizers, you must explicitly
   set them as above.

.. note::
   The following 4 minimizers need a local optimizer selected to run. This has been set to use `LD_LBFGS`.

   .. code-block:: rst

    [MINIMIZERS]
    nlopt: AUGLAG
           AUGLAG_EQ
           G_MLSL_LDS
           G_MLSL

.. _paramonte:

Paramonte (``paramonte``)
=========================

`Paramonte <https://www.cdslab.org/paramonte/index.html>`__ is a
serial/parallel library of Monte Carlo routines for sampling mathematical
objective functions of arbitrary-dimensions. We currently support:

* `ParaDRAM Sampler <https://www.cdslab.org/pubs/2020_Shahmoradi_I.pdf>`__ (:code:`paraDram_sampler`)

**Licence** Paramonte is available under an `MIT licence <https://github.com/cdslaborg/paramonte/blob/main/LICENSE.md>`__

The Paramonte minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    paramonte: paraDram_sampler

.. warning::
   The additional dependency Paramonte must be installed to use these minimizers;
   see :ref:`extra_dependencies`.

.. _ralfit:

RALFit (``ralfit``)
===================

`RALFit <https://ralfit.readthedocs.io/projects/Fortran/en/latest/>`__
is a nonlinear least-squares solver, the development of which was funded
by the EPSRC grant `Least-Squares: Fit for the Future`.  RALFit is designed to be able
to take advantage of higher order derivatives, although only first
order derivatives are currently utilized in FitBenchmarking.

* Gauss-Newton, trust region method (:code:`gn`)
* Hybrid Newton/Gauss-Newton, trust region method (:code:`hybrid`)
* Newton, trust region method (:code:`newton`)
* Newton-tensor, trust region method (:code:`newton-tensor`)
* Gauss-Newton, regularization (:code:`gn_reg`)
* Hybrid Newton/Gauss-Newton, regularization (:code:`hybrid_reg`)
* Newton, regularization (:code:`newton_reg`)
* Newton-tensor, regularization (:code:`newton-tensor_reg`)

Note that the Newton-tensor methods take significantly longer than the other
options to run (but may give a better solution in some cases).  For this
reason, they are not included in the default minimizers for RALFit, but
must be turned on in the options file.

**Links** `Github - RALFit <https://github.com/ralna/ralfit/>`__. RALFit's Documentation on: `Gauss-Newton/Hybrid models <https://ralfit.readthedocs.io/projects/Fortran/en/latest/method.html#the-models>`__,  `the trust region method <https://ralfit.readthedocs.io/projects/Fortran/en/latest/method.html#the-trust-region-method>`__ and  `The regularization method <https://ralfit.readthedocs.io/projects/C/en/latest/method.html#regularization>`__

**Licence** RALFit is available under a `3-clause BSD Licence <https://github.com/ralna/RALFit/blob/master/LICENCE>`__

The RALFit minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    ralfit: gn
            gn_reg
            hybrid
            hybrid_reg

.. warning::
   The external package RALFit must be installed to use these minimizers.

.. _scipy:

SciPy (``scipy``)
=================

`SciPy <https://www.scipy.org>`__ is the standard python package for mathematical
software.  In particular, we use the `minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`__
solver for general minimization problems from the optimization chapter of
SciPy's library. Currently we only use the algorithms that do not require
Hessian information as inputs.

* `Nelder-Mead algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html>`__ (:code:`Nelder-Mead`)
* `Powell algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-powell.html>`__ (:code:`Powell`)
* `Conjugate gradient algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cg.html>`__ (:code:`CG`)
* `BFGS algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-bfgs.html>`__ (:code:`BFGS`)
* `Newton-CG algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-newtoncg.html>`__  (:code:`Newton-CG`)
* `L-BFGS-B algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html>`__ (:code:`L-BFGS-B`)
* `Truncated Newton (TNC) algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-tnc.html>`__ (:code:`TNC`)
* `Sequential Least SQuares Programming <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html>`__ (:code:`SLSQP`)
* `Constrained Optimization BY Linear Approximations <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cobyla.html>`__ (:code:`COBYLA`)
* `Newton-CG trust-region <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustncg.html>`__  (:code:`trust-ncg`)
* `Nearly exact trust-region <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustexact.html>`__  (:code:`trust-exact`)
* `Newton Generalized Lanczos Trust Region <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustkrylov.html>`__  (:code:`trust-krylov`)
* `Trust-region for constrained optimization <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-trustconstr.html>`__  (:code:`trust-constr`)
* `Dog-leg trust-region <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-dogleg.html>`__ (:code:`dogleg`)

**Links** `Github - SciPy minimize <https://github.com/scipy/scipy/blob/master/scipy/optimize/_minimize.py>`__

**Licence** Scipy is available under a `3-clause BSD Licence <https://github.com/scipy/scipy/blob/master/LICENSE.txt>`__.  Individual packages may have their own (compatible) licences, as listed `here <https://github.com/scipy/scipy/blob/master/LICENSES_bundled.txt>`__.

The SciPy minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    scipy: Nelder-Mead
           Powell
           CG
           BFGS
           Newton-CG
           L-BFGS-B
           TNC
           SLSQP
           COBYLA
           trust-ncg
           trust-exact
           trust-krylov
           trust-constr
           dogleg

.. note::
   The Hessian enabled solvers are not run by default when `scipy` software is selected. In order to run these minimizers, you must explicitly
   set them as above.

.. _scipy-ls:

SciPy LS (``scipy_ls``)
=======================

`SciPy <https://www.scipy.org>`__ is the standard python package for mathematical
software.  In particular, we use the `least_squares <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html#scipy.optimize.least_squares>`__
solver for Least-Squares minimization problems from the optimization chapter
of SciPy's library.

* Levenberg-Marquardt with supplied Jacobian (:code:`lm-scipy`)  - a wrapper around MINPACK
* The Trust Region Reflective algorithm (:code:`trf`)
* A dogleg algorithm with rectangular trust regions (:code:`dogbox`)

**Links** `Github - SciPy least_squares <https://github.com/scipy/scipy/blob/master/scipy/optimize/_lsq/least_squares.py>`__

**Licence** Scipy is available under a `3-clause BSD Licence <https://github.com/scipy/scipy/blob/master/LICENSE.txt>`__.  Individual packages many have their own (compatible) licences, as listed `here <https://github.com/scipy/scipy/blob/master/LICENSES_bundled.txt>`__.

The SciPy least squares minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    scipy_ls: lm-scipy
              trf
              dogbox

.. _scipy-go:

SciPy GO (``scipy_go``)
=======================

`SciPy <https://www.scipy.org>`__ is the standard python package for mathematical
software.  In particular, we use the `Global Optimization <https://docs.scipy.org/doc/scipy/reference/optimize.html#global-optimization>`__
solvers for global optimization problems from the optimization chapter
of SciPy's library.

* `Differential Evolution (derivative-free) <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution.html#scipy.optimize.differential_evolution>`__ (:code:`differential_evolution`)
* `Simplicial Homology Global Optimization (SHGO) <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.shgo.html#scipy.optimize.shgo>`__ (:code:`shgo`)
* `Dual Annealing <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.dual_annealing.html#scipy.optimize.dual_annealing>`__ (:code:`dual_annealing`)

**Links** `Github - SciPy optimization <https://github.com/scipy/scipy/blob/master/scipy/optimize/>`__

**Licence** Scipy is available under a `3-clause BSD Licence <https://github.com/scipy/scipy/blob/master/LICENSE.txt>`__.  Individual packages may have their own (compatible) licences, as listed `here <https://github.com/scipy/scipy/blob/master/LICENSES_bundled.txt>`__.

The SciPy global optimization minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    scipy_go: differential_evolution
              shgo
              dual_annealing

.. note::
   The shgo solver is particularly slow running and should generally be avoided. As a result, this solver is
   not run by default when `scipy_go` software is selected. In order to run this minimizer, you must explicitly
   set it as above.

.. _theseus:

Theseus (``theseus``)
=======================

`Theseus <https://sites.google.com/view/theseus-ai/>`__ is an efficient application-agnostic library for building custom nonlinear optimization
layers in PyTorch to support constructing various problems in robotics and vision as end-to-end
differentiable architectures.

* Levenberg Marquardt (:code:`Levenberg_Marquardt`)
* Gauss Newton (:code:`Gauss-Newton`)

**Links** `Paper- Theseus optimization <https://arxiv.org/pdf/2207.09442.pdf/>`__

**Licence** Theseus is available under a `MIT licence <https://github.com/facebookresearch/theseus/blob/main/LICENSE>`__.

The theseus minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    theseus: Levenberg_Marquardt
             Gauss-Newton

.. note::
   We strongly recommend you install Theseus in a venv or conda environment with Python 3.7-3.9
