.. _minimizer_option:

#################
Minimizer Options
#################

This section is used to declare the minimizers to use for each fitting
software.

.. warning::

   Options set in this section will only have an effect if the related
   software is also set in :ref:`fitting_option` (either explicitly, or
   as a default option).

Bumps (:code:`bumps`)
---------------------

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

The Bumps minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    bumps: amoeba
           lm-bumps
           newton
           de
           mp

.. warning::
   The additional dependency Bumps must be installed for this to be available;
   See :ref:`extra_dependencies`.	 
	   

DFO (``dfo``)
-----------------------

There are two Derivative-Free Optimization packages, `DFO-LS <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ and
`DFO-GN <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_.
They are derivative free optimization solvers that were developed by Lindon Roberts at the University
of Oxford, in conjunction with NAG.  They are particularly well suited for solving noisy problems.

FitBenchmarking currently supports the DFO minimizers:

* `Derivative-Free Optimizer for Least Squares <http://people.maths.ox.ac.uk/robertsl/dfols/userguide.html>`_ (:code:`dfols`)

* `Derivative-Free Gauss-Newton Solver <http://people.maths.ox.ac.uk/robertsl/dfogn/userguide.html>`_ (:code:`dfogn`)

 **Links** `GitHub - DFO-GN <https://github.com/numericalalgorithmsgroup/dfogn>`_ `GitHub - DFO-LS <https://github.com/numericalalgorithmsgroup/dfols>`_

The DFO minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    dfo: dfols
         dfogn

.. warning::
   Additional dependencies `DFO-GN` and `DFO-LS` must be installed for
   these to be available;
   See :ref:`extra_dependencies`.	 

	 
GSL (``gsl``)
-------------

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

.. _MantidMinimizers:
   
Mantid (``mantid``)
-------------------

`Mantid <https://www.mantidproject.org>`_ is a framework created to
manipulate and analyze neutron scattering and muon spectroscopy data.
It has support for a number of minimizers, most of which are from GSL.

* `BFGS <https://docs.mantidproject.org/nightly/fitting/fitminimizers/BFGS.html>`_ (:code:`BFGS`)

* `Conjugate gradient (Fletcher-Reeves) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/FletcherReeves.html>`_ (:code:`Conjugate gradient (Fletcher-Reeves imp.)`)

* `Conjugate gradient (Polak-Ribiere) <https://docs.mantidproject.org/nightly/fitting/fitminimizers/PolakRibiere.html>`_ (:code:`Conjugate gradient (Polak-Ribiere imp.)`)

* `Damped GaussNewton <https://docs.mantidproject.org/nightly/fitting/fitminimizers/DampedGaussNewton.html>`_ (:code:`Damped GaussNewton`)

* `Levenberg-Marquardt algorithm <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardt.html>`_ (:code:`Levenberg-Marquardt`)

* `Levenberg-Marquardt MD <https://docs.mantidproject.org/nightly/fitting/fitminimizers/LevenbergMarquardtMD.html>`_ (:code:`Levenberg-MarquardtMD`) - An implementation of Levenberg-Marquardt intended for MD workspaces, where work is divided into chunks to achieve a greater efficiency for a large number of data points.

* `Simplex <https://docs.mantidproject.org/nightly/fitting/fitminimizers/Simplex.html>`_ (:code:`simplex`)

* `SteepestDescent <https://docs.mantidproject.org/nightly/fitting/fitminimizers/GradientDescent.html>`_ (:code:`SteepestDescent`)

* `Trust Region <https://docs.mantidproject.org/nightly/fitting/fitminimizers/TrustRegion.html>`_ (:code:`Trust Region`) - An implementation of one of the algorithms available in RALFit.

 **Links** `GitHub - Mantid <https://github.com/mantidproject/mantid>`_ `Mantid's Fitting Docs <https://docs.mantidproject.org/nightly/algorithms/Fit-v1.html>`_

The Mantid minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    mantid: BFGS
            Conjugate gradient (Fletcher-Reeves imp.)
            Conjugate gradient (Polak-Ribiere imp.)
            Damped GaussNewton
            Levenberg-Marquardt
            Levenberg-MarquardtMD
            Simplex
            SteepestDescent
            Trust Region

.. warning::
   The external package Mantid must be installed to use these minimizers.
	    
Minuit (``minuit``)
-------------------

CERN developed the `Minuit <http://seal.web.cern.ch/seal/snapshot/work-packages/mathlibs/minuit/>`_ package to find the minimum value of a multi-parameter function, and also to compute the uncertainties.
We interface via the python interface `iminuit <https://iminuit.readthedocs.io>`_

* `Minuit's MIGRAD <https://root.cern.ch/root/htmldoc/guides/minuit2/Minuit2.pdf>`_ (:code:`minuit`)

**Links** `Github - iminuit <https://github.com/scikit-hep/iminuit>`_

The Minuit minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    minuit: minuit

.. warning::
   The additional dependency Minuit must be installed for this to be available;
   See :ref:`extra_dependencies`.	 

    
RALFit (``ralfit``)
-------------------

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

The RALFit minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    ralfit: gn
            gn_reg
            hybrid
            hybrid_reg

.. warning::
   The external package RALFit must be installed to use these minimizers.

SciPy (``scipy``)
-----------------

`SciPy <https://www.scipy.org>`_ is the standard python package for mathematical
software.  In particular, we use the `minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`_
solver for general minimization problems from the optimization chapter the
SciPy's library. Currently we only use the algorithms that do not require
Hessian information as inputs.

* `Nelder-Mead algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-neldermead.html>`_ (:code:`Nelder-Mead`)
* `Powell algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-powell.html>`_ (:code:`Powell`)
* `Conjugate gradient algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-cg.html>`_ (:code:`CG`)
* `BFGS algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-bfgs.html>`_ (:code:`BFGS`)
* `Newton-CG algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-newtoncg.html>`_  (:code:`Newton-CG`)
* `L-BFGS-B algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html>`_ (:code:`L-BFGS-B`)
* `Truncated Newton (TNC) algorithm <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-tnc.html>`_ (:code:`TNC`)
* `Sequential Least SQuares Programming <https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html>`_ (:code:`SLSQP`)

**Links** `Github - SciPy minimize <https://github.com/scipy/scipy/blob/master/scipy/optimize/_minimize.py>`_

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

SciPy LS (``scipy_ls``)
-----------------------

`SciPy <https://www.scipy.org>`_ is the standard python package for mathematical
software.  In particular, we use the `least_squares <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html#scipy.optimize.least_squares>`_
solver for Least-Squares minimization problems from the optimization chapter
the SciPy's library.

* Levenberg-Marquardt with supplied Jacobian (:code:`lm-scipy`)  - a wrapper around MINPACK
* Levenberg-Marquardt with no Jacobian passed (:code:`lm-scipy-no-jac`)  - as above, but using MINPACK's approximate Jacobian
* The Trust Region Reflective algorithm (:code:`trf`)
* A dogleg algorithm with rectangular trust regions (:code:`dogbox`)

**Links** `Github - SciPy least_squares <https://github.com/scipy/scipy/blob/master/scipy/optimize/_lsq/least_squares.py>`_

The SciPy least squares minimizers are set as follows:

.. code-block:: rst

    [MINIMIZERS]
    scipy_ls: lm-scipy-no-jac
              lm-scipy
              trf
              dogbox
