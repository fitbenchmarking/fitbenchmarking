.. _controllers:

#######################
Adding Fitting Software
#######################

Controllers are used to interface FitBenchmarking with the various fitting
packages. Controllers are responsible for converting the problem into a format
that the fitting software can use, and converting the result back to a
standardised format (numpy arrays). As well as this, the controller must be
written so that the fitting is separated from the preparation wherever possible
in order to give accurate timings for the fitting. Supported controllers are
found in ``fitbenchmarking/controllers/``.

In order to add a new controller, you will need to:

1. Give the software a name ``<software_name>``.  This will be used by users when
   selecting this software.

2. Create ``fitbenchmarking/controllers/<software_name>_controller.py``
   which contains a new subclass of
   :class:`~fitbenchmarking.controllers.base_controller.Controller`.

   .. note::
      Please note that if the fitting package being added uses Matlab, then the
      new controller should also inherit from the mixin class
      :class:`~fitbenchmarking.controllers.matlab_mixin.MatlabMixin`.

      .. autoclass:: fitbenchmarking.controllers.matlab_mixin.MatlabMixin
          :members: py_to_mat
          :noindex:

   The new controller should implement four functions, as well as initializing the dictionary ``algorithm_check``:

  - .. autoattribute:: fitbenchmarking.controllers.base_controller.Controller.algorithm_check
               :noindex:  

  -  .. automethod:: fitbenchmarking.controllers.base_controller.Controller.__init__()
                     :noindex:
  -  .. automethod:: fitbenchmarking.controllers.base_controller.Controller.setup()
              :noindex:
  -  .. automethod:: fitbenchmarking.controllers.base_controller.Controller.fit()
              :noindex:
  -  .. automethod:: fitbenchmarking.controllers.base_controller.Controller.cleanup()
              :noindex:

   By default, a controller does not accept Jacobian or Hessian information. If the controller
   being added can use hessians and/or jacobians, then the following controller attributes should
   be set:

   - .. autoattribute:: fitbenchmarking.controllers.base_controller.Controller.jacobian_enabled_solvers()
               :noindex:  
   - .. autoattribute:: fitbenchmarking.controllers.base_controller.Controller.hessian_enabled_solvers()
               :noindex: 

3. Add the new software to the default options, following the instructions in
   :ref:`options_extend`.

Your new software is now fully hooked in with FitBenchmarking, and you can compare
it with the current software.  You are encouraged to contribute this to the
repository so that other can use this package.  To do this need to follow our
:ref:`guidelines` and our :ref:`workflow`, and you'll also need to

4. Document the available minimizers (see :ref:`fitting_option`, :ref:`minimizer_option`),
   including licencing information, if appropriate.
   Note: make sure that you use ``<software_name>`` in these places so that the
   software links in the HTML tables link correctly to the documentation.
   Add the software to ``examples/all_software.ini``.

   You should also ensure that the available minimizers are catagorised correctly in ``self.algorithm_check``
   using the :ref:`algorithm type <algorithm_type>` options. Please refer to the :ref:`algorithms`
   page for more information about each algorithm type.

5. Create tests for the software in
   ``fitbenchmarking/controllers/tests/test_controllers.py``. If the package
   is ``pip`` installable then add the tests to the ``DefaultControllerTests`` class
   and if not add to the ``ExternalControllerTests`` class.
   Unless the new controller is more complicated than the currently available
   controllers, this can be done by following the example of the others.

6. If the software is deterministic, add the software to the regression tests in
   ``fitbenchmarking/systests/test_regression.py``. 
   
7. If `pip` installable add to ``install_requires`` in ``setup.py`` and
   add to the installation step in ``.github/workflows/release.yml``.
   If not, document the installation procedure in :ref:`external-instructions`
   and update the ``FullInstall`` Docker Container -- the main developers will
   help you with this.

.. note::
   For ease of maintenance, please add new controllers to a list of
   software in alphabetical order.


The :class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`,  :class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc` and :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new minimizers, you will find it helpful to make use of the
following members of the
:class:`~fitbenchmarking.parsing.fitting_problem.FittingProblem`, subclasses of
:class:`~fitbenchmarking.cost_func.base_cost_func.CostFunc` and subclasses of
:class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` classes:

.. currentmodule:: fitbenchmarking.parsing.fitting_problem
.. autoclass:: fitbenchmarking.parsing.fitting_problem.FittingProblem
          :members: eval_model, data_x, data_y, data_e, set_value_ranges
          :noindex:

.. currentmodule:: fitbenchmarking.cost_func.base_cost_func
.. autoclass:: fitbenchmarking.cost_func.base_cost_func.CostFunc
          :members: eval_cost
          :noindex:

.. currentmodule:: fitbenchmarking.jacobian.base_jacobian
.. autoclass:: fitbenchmarking.jacobian.base_jacobian.Jacobian
          :members: eval, eval_cost
          :noindex:
