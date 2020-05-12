.. _jacobian_extend:

####################
Adding new Jacobians
####################

*This section describes how to add further methods to approximate the Jacobian within FitBenchmarking*
within FitBenchmark.*

In order to add a new Jacobian evaluation method, you will need to:

1. Give the Jacobian a name using the following convention `<jac_method>` and
   `<num_method>`.
2. Create ``fitbenchmarking/jacobian/<jac_method>_<num_method>_jacobian.py``
   which contains a new subclass of ``Jacobian``
   (from ``base_jacobian.py``).
   Then implement the method ``eval()``, which evaluates the Jacobian.

3. Document the available Jacobians by: 
  * updating the docs for :ref:`jacobian` in ``docs/source/users/jacobian.rst`` 
  * updating ``fitbenchmarking/utils/default_options.ini`` 
  * updating any example files in the ``example_scripts`` directory

4. Create tests for the Jacobian evaluation in
   ``fitbenchmarking/jacobian/tests/test_jacobians.py``.
