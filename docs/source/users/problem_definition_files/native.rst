.. _native:

******************
Native File Format
******************

In FitBenchmarking, the native file format is used to read IVP, Mantid, and
SASView problems.

In this format, data is separated from the function. This allows running the
same dataset against multiple different models to assess which is the most
appropriate.

Examples of native problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/Data_Assimilation/lorentz.txt

.. literalinclude:: ../../../../examples/benchmark_problems/Muon/Muon_HIFI_113856.txt

.. literalinclude:: ../../../../examples/benchmark_problems/SAS_modelling/SASView_Simple_Shapes_1D/1D_cylinder_neutron_def0.txt

These examples show the basic structure in which the file starts with a comment
indicating it is a FitBenchmark problem followed by key-value pairs. Available
keys are described below:

software
  Either 'IVP', 'Mantid', 'SasView', or 'Horace' (case insensitive).

  This defines whether to use an IVP format, Mantid, or SasView to generate the model.
  The 'Mantid' software also supports Mantid's MultiFit functionality, which
  requires the parameters listed here to be defined slightly differently.
  More information can be found in :ref:`multifit`.

  For information on the 'Horace' format, see :ref:`horace_format`.

  **Licence** Mantid is available under a
  `GPL-3 Licence <https://github.com/mantidproject/mantid/blob/master/LICENSE.txt>`_.
  The component of SasView we use is SasModels, which is available under a
  `BSD 3-clause <https://github.com/SasView/sasmodels/blob/master/LICENSE.txt>`_ licence.

name
  The name of the problem.

  This will be used as a unique reference so should not match other names in the
  dataset. A sanitised version of this name will also be used in filenames with
  commas stripped out and spaces replaced by underscores.

description
  A description of the dataset.

  This will be displayed in the Problem Summary Pages and Fitting Reports produced by a
  benchmark.

input_file
  The name of a file containing the data to fit.

  The file must be in a subdirectory named ``data_files``, and should have the form::

     header

     x11 [x12 [x13 ...]] y11 [y12 [y13 ...]] [e11 [e12 ...]]
     x21 [x22 [x23 ...]] y21 [y22 [y23 ...]] [e21 [e22 ...]]
     ...

  Mantid uses the convention of ``# X Y E`` as the header and SASView uses
  the convention ``<X>   <Y>   <E>``, although neither of these are enforced.
  The error column is optional in this format.

  If the data contains multiple inputs or outputs, the header must be written
  in one of the above conventions with the labels as "x", "y", or "e" followed by
  a number. An example of this can be seen in
  ``examples/benchmark_problems/Data_Assimilation/data_files/lorentz.txt``

plot_scale
  The scale of the x and y axis for the plots. The options are 'loglog', 'logy', 'logx' and 'linear'. If this
  is not set it will default to 'linear'.

function
  This defines the function that will be used as a model for the fitting.

  Inside FitBenchmarking, this is passed on to the specified software and, as
  such, the format is specific to the package we wish to use, as described below.

  **IVP**

  The IVP parser allows a user to define ``f`` in the following equation:

  .. math:: x' = f(t, x, *args)

  To do this we use a python module to define the function. As in the above
  formula, the function can take the following arguments:

  - *t* (float): The time to evaluate at
  - *x* (np.array): A value for x to evaluate at
  - *\*args* (floats): The parameters to fit

  To link to this function we use a function string with the following
  parameters:

  - *module*: The path to the module
  - *func*: The name of the function within the module
  - *step*: The time step that the input data uses
    (currently only fixed steps are supported - if you need
    varying time steps please raise an issue on our GitHub)
  - *\*args*: Starting values for the parameters

  **Mantid**

  A Mantid function consists of one or more base functions separated by a semicolon.
  This allows for a powerful way of describing problems, which may have multiple
  components such as more than one Gaussian and a linear background.

  To use one of the base functions in Mantid, please see the list available
  `here <https://docs.mantidproject.org/nightly/fitting/fitfunctions/categories/FitFunctions.html>`__.

  *Note: Any non-standard arguments (e.g. ties, constraints, fixes, ...) will
  only work with Mantid fitting software. Using other minimizers to fit these
  problems will result in the non-standard arguments being ignored.*

  **SASView**

  SASView functions can be any of
  `these <http://www.sasview.org/docs/user/qtgui/Perspectives/Fitting/models/index.html>`__.

  **Horace**

  The Horace functions are defined here :ref:`horace_format` .

jacobian
  This is to define a dense jacobian function, or a sparse jacobian function, or both.
  The parser for this function allows the user to define ``g`` in the following:

  .. math:: \nabla_p f(x, *args) = g(x, *args)

  To do this we use a python module, where the user can define a dense jacobian function
  and a sparse jacobian function (or just one of the two). As in the above formula,
  both functions can take the following arguments:

  - *x* (np.array): A value for x to evaluate at
  - *\*args* (floats): The parameters to fit

  To link to this functions we use a string with the following parameters:

  - *module*: The path to the module
  - *dense_func*: The name of the dense jacobian function within the module
  - *sparse_func*: The name of the sparse jacobian function within the module

The sparse jacobian function provided must return a matrix in sparse format
(e.g. coo, csr, crs), otherwise an error will be thrown.

fit_ranges
  This specifies the region to be fit.

  It takes the form shown in the example, where the first number
  is the minimum in the range and the second is the maximum.

parameter_ranges
  An optional setting which specifies upper and lower bounds for
  parameters in the problem.

  Similarly to ``fit_ranges``, it takes the form where the first number
  is the minimum in the range and the second is the maximum.

  Currently in Fitbenchmarking, problems with `parameter_ranges` can
  be handled by SciPy, Bumps, Minuit, Mantid, Matlab Optimization Toolbox,
  DFO, Levmar and RALFit fitting software. Please note that the following
  Mantid minimizers currently throw an exception when `parameter_ranges`
  are used: BFGS, Conjugate gradient (Fletcher-Reeves imp.),
  Conjugate gradient (Polak-Ribiere imp.) and SteepestDescent.
