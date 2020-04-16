.. _controllers:

#######################
Adding Fitting Software
#######################

*This section describes how to add additional software to benchmark against
the available problems.*

In FitBenchmarking, controllers are used to interface into the various fitting
softwares. Controllers are responsible for converting the problem into a format
that the fitting software can use, and converting the result back to a
standardised format (numpy arrays). As well as this, the controller must be
written so that the fitting is separated from the preparation wherever possible
in order to give accurate timings for the fitting. Examples of these
controllers can be found in ``fitbenchmarking/fitting/controllers``.

Fitting software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to add a new controller, you will need to:

1. Give the software a name `<software_name>` this will be used by users when
   selecting this software.
2. Create ``fitbenchmarking/fitting/controllers/<software_name>_controller.py``
   which contains a new subclass of ``BaseSoftwareController``
   (from ``base_controller.py``).
   This should implement 4 functions:

   -  ``__init__()``: Initialise anything that is needed specifically for the
      software, do any work that can be done without knowledge of the
      minimizer to use, or function to fit, and call ``super().__init__()``.
   -  ``setup()``: Do any work that must be done only after knowing the
      minimizer to use and the function to fit. E.g. creating function wrappers
      around a callable.
   -  ``fit()``: Run the fitting. This will be timed so should include only
      what is needed to fit the data.
   -  ``cleanup()``: Convert the results into the expected numpy arrays,
      error flags and store them in the results variables
      (``self.results``, ``self.final_params``, ``self.flag``).
      The flag corresponds to the following messages::

         0: "Successfully converged",
         1: "Software reported maximum number of iterations exceeded",
         2: "Software run but didn't converge to solution",
         3: "Software raised an exception".

4. Document the available minimizers (currently done by adding to
   ``fitbenchmarking/utils/default_options.ini`` and any example files in
   the ``example_scripts`` directory)

5. Create tests for the software in
   ``fitbenchmarking/fitting/tests/test_controllers.py``.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.

.. note::
   For ease of maintenance, please add new controllers to a list of software in alphabetical order.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new minimizers, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` class:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
	          :noindex:
		  :members: eval_f, eval_r, eval_r_norm, eval_j,
			data_x, data_y, data_e, starting_values


