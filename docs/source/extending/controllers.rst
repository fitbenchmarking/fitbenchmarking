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
controllers can be found in ``fitbenchmarking/controllers``.

Fitting software requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to add a new controller, you will need to:

1. Give the software a name `<software_name>` this will be used by users when
   selecting this software.
2. Create ``fitbenchmarking/controllers/<software_name>_controller.py``
   which contains a new subclass of ``BaseSoftwareController``
   (from ``base_controller.py``).
   This should implement 4 functions:

   -  ``__init__()``: Initialise anything that is needed specifically for the
      software, do any work that can be done without knowledge of the
      minimizer to use, or function to fit, and call ``super().__init__()``. In this
      function, you must initialize the a dictionary, ``self.algorithm_type``, such that
      the keys are given by:

        - 'all' - all minimizers
        - 'ls' - least-squares fitting algorithms
        - 'deriv_free' - derivative free algorithms (these are algorithms that
                         do not require an information about derivatives. For
                         example, the 'Simplex' method in 'Mantid' does not
                         require derivative information but 'lm-scipy-no-jac' in
                         'scipy_ls' does but the derivative is handle internally
                         within the sofware package)
        - 'general' - minimizers which solve a generic `min f(x)`
      and the values as a list of minimizer for that specific controller that fit into
      each of the above categories. See for example the ``GSL`` controller.
   -  ``setup()``: Do any work that must be done only after knowing the
      minimizer to use and the function to fit. E.g. creating function wrappers
      around a callable.
   -  ``fit()``: Run the fitting. This will be timed so should include only
      what is needed to fit the data.
   -  ``cleanup()``: Convert the results into the expected numpy arrays,
      error flags and store them in the results variables
      (``self.results``, ``self.final_params``, ``self.flag``).
      The flag corresponds to the following messages:

      .. automethod:: fitbenchmarking.controllers.base_controller.Controller.flag

4. Document the available minimizers (see :ref:`options`, :ref:`options_extend`
   and any example files in the ``example_scripts`` directory). For none ``pip`` installable software please comment out the software in the default options file but add it to ``examples/all_softwares.ini``.

5. Create tests for the software in
   ``fitbenchmarking/controllers/tests/test_controllers.py``. If the package
   is ``pip`` installable then add the tests to ``DefaultControllerTests`` class
   and if not add to the ``ExternalControllerTests`` class.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.

6. If `pip` installable add to ``install_requires`` in ``setup.py`` otherwise follow
   the same installation procedure for the external fitting softwares found in
   :ref:`external-instructions`

7. In the :ref:`Minimizers` page of the :ref:`how` page, update with the
   new software and minimizers following the structure there. Note: make
   sure that you use `<software_name>` in :ref:`Minimizers` so that the
   software links in the HTML tables link correctly to the documentation.

8. At the bottom of :doc:`main index page <../index>`, add the logo of the
   of the software package in the `Currently Benchmarking` section.

.. note::
   For ease of maintenance, please add new controllers to a list of
   software in alphabetical order.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new minimizers, you will find it helpful to make use of the
following members of the :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem` and subclasses of :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` classes:


.. currentmodule:: fitbenchmarking.jacobian.base_jacobian
.. autoclass:: fitbenchmarking.jacobian.base_jacobian.Jacobian
          :members: eval

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
	          :noindex:
		  :members: eval_f, eval_r, eval_r_norm,
			data_x, data_y, data_e, starting_values
