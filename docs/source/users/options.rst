.. _options:

#######################
FitBenchmarking Options
#######################

FitBenchmarking is controlled by 2 sets of options,
which are controlled in 2 ways, software arguments and software options.

Software Arguments
==================
The first set of options are set in the example scripts and used as arguments
for the software.
These include:

:py:`software`
------------
The software to use in fitting as a string or list of strings.
Selected softwares will be benchmarked.

Available options are :py:`mantid`, :py:`sasview`, and :py:`scipy`.

:py:`results_dir`
---------------
A path to the directory where the results should be stored.
If :py:`None`, a results directory will be created at ``./results``.

:py:`use_errors`
--------------
Bool to select whether to use errors in the fitting process or not.

:py:`color_scale`
--------------
The mapping from relative value to colour in the results table.

This should be in the form of a list of 2-tuples,
where the first value in each 2-tuple is a threshold value (float)
and the second value is a ranking (string) linked to definitions in the
``color_definitions.txt`` file.

Available rankings are: :py:`ranking-top-1`, :py:`ranking-top-2`,
:py:`ranking-med-3`, :py:`ranking-low-4`, and :py:`ranking-low-5`.

e.g.

.. code-block:: python

  [(1.1, 'ranking-top-1'),
   (1.33, 'ranking-top-2'),
   (1.75, 'ranking-med-3'),
   (3, 'ranking-low-4'),
   (float('nan'), 'ranking-low-5')]


:py:`problem_sets`
----------------
The dataset(s) to use as a list of strings.
This is used in the example script to get the data directory,
which is then in turn used in the software.

Software Options
================
The second set of options is controlled by the software_options argument.
These can be set in either the :py:`software_options` dictionary,
or an options file (with the filename in the :py:`software_options` dictionary).

Note: If you are using the example script,
the options filename can be passed in as the first argument.

The options that can be used with the options file are:

:py:`minimizers`
----------------
Minimizers to be used with the software can be specified.
This should be a dictionary with key value as the software,
and value as a list of minimizers.

e.g.

.. code-block:: python

    {'scipy': ['dogbox' ,'lm', 'trf'],
     'sasview': ['amoeba', ...]
    }

Available minimizers are:

Mantid:
  - :py:`BFGS`
  - :py:`Conjugate gradient (Fletcher-Reeves imp.)`
  - :py:`Conjugate gradient (Polak-Ribiere imp.)`
  - :py:`Damped GaussNewton`
  - :py:`Levenberg-Marquardt`
  - :py:`Levenberg-MarquardtMD`
  - :py:`Simplex`
  - :py:`SteepestDescent`
  - and :py:`Trust Region`

  Information about these can be found on the
  `Mantid documentation
  <https://docs.mantidproject.org/nightly/fitting/fitminimizers/>`__


SasView (bumps):
  - :py:`amoeba`
  - :py:`de`
  - :py:`lm`
  - :py:`mp`
  - :py:`newton`
  - and :py:`pt`

  Information about these can be found on the
  `Bumps documentation
  <https://bumps.readthedocs.io/en/latest/guide/optimizer.html>`__


Scipy:
  - :py:`dogbox`
  - :py:`lm`
  - and :py:`trf`

  Information about these can be found on the
  `Scipy documentation
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html>`__

:py:`comparison_mode`
---------------------
The comparison mode is used when displaying results to select the value
displayed in the tables.

Available options are :py:`abs`, :py:`rel`, or :py:`both`.

:py:`abs`
  Return absolute values.
  This is the result you would expect from running the fitting independently.

:py:`rel`
  Return relative values.
  All results are scaled so that the best performing has a value of 1,
  i.e. results indicate the factor difference between the best performing
  minimizer and each of the other minimizers.

:py:`both`
  Return both absolute and relative values.
  Values will be shown as an absolute value followed by a relative value in
  parentheses.
