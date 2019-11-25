.. _options:

#######################
FitBenchmarking Options
#######################

FitBenchmarking is controlled by a set of options that can be controlled in
3 different ways.
In order from lowest priority to highest these are:

- The default options.
- An options file.
- Options set in a script.

The default options are a complete set of options with sensible values.
These will be used when no other values are given for any of the options,
the values for these can be seen at the end of this document.

The options file must be a `.ini` file, and a good reference for this can be
found in the examples, as well as at the bottom of this document.


Minimizers
----------

Minimizers to be used with the software can be specified via the MINIMIZERS
section of the options file.

e.g.

.. code-block:: python

    [MINIMIZERS]
    scipy: dogbox
           lm
           trf
    sasview: amoeba
             ...

Available minimizers are:

Mantid:
  - `BFGS`
  - `Conjugate gradient (Fletcher-Reeves imp.)`
  - `Conjugate gradient (Polak-Ribiere imp.)`
  - `Damped GaussNewton`
  - `Levenberg-Marquardt`
  - `Levenberg-MarquardtMD`
  - `Simplex`
  - `SteepestDescent`
  - and `Trust Region`

  Information about these can be found on the
  `Mantid documentation
  <https://docs.mantidproject.org/nightly/fitting/fitminimizers/>`__


Minuit:
  - `minuit`

  Information about this can be found on the
  `Minuit documentation
  <http://iminuit.readthedocs.org>`__


SasView (bumps):
  - `amoeba`
  - `de`
  - `lm`
  - `mp`
  - `newton`
  - and `pt`

  Information about these can be found on the
  `Bumps documentation
  <https://bumps.readthedocs.io/en/latest/guide/optimizer.html>`__


Scipy:
  - `dogbox`
  - `lm`
  - and `trf`


  Information about these can be found on the
  `Scipy documentation
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html>`__


DFO-GN:
  - `dfogn`

  Information about this can be found on the
  `DFO-GN documentation
  <http://people.maths.ox.ac.uk/robertsl/dfogn/>`__


RALfit:
  - `gn` (Gauss-Newton within a trust region)
  - `gn_reg` (Gauss-Newton with regularization)
  - `hybrid` (Hybrid method within a trust region)
  - `hybrid_reg` (Hybrid method with regularization)

  Information about this can be found on the
  `RALfit documentation
  <https://ralfit.readthedocs.io/projects/Python/en/latest/>`__

----------------
Options template
----------------
This is a template you can use which contains information on each option
available, as well as the defaults.


.. prettyprintvalue::
   :module: fitbenchmarking.utils.options
   :class: Options
   :var: DEFAULTS
