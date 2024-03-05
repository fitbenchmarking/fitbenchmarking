.. _install_instructions:

#####################################
Install Instructions for Contributors
#####################################

Please see below for the recommended install instructions
for new contributors:

1. Before installing, it is recommended that you create an empty
   virtual environment. For more information about installing
   packages using virtual environments please see 
   `here <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`__.

2. To ensure that you are working with the latest version of the
   code, you should install Fitbenchmarking from source. For
   details on how to do this, please see :ref:`installing_from_source`.

   .. note::
        The `editable` flag should be used when installing from source, like 
        ``pip install -e ...``, so that changes made to the cloned code 
        are immediately reflected in the imported package.

3. So that you are able to run all tests locally, all extra dependencies and
   external software should be installed. Please see :ref:`extra_dependencies`
   and :ref:`external-instructions` for instructions on how to do this.

   .. note::
        Please note that if you are using WSL, Matlab is likely
        to be difficult to install so it is recommended that you use an alternative
        operating system if you are working on Matlab related issues. 

        Additionally, the tests run through Github do not currently include Matlab
        fitting software, so please ensure tests are run locally before submitting
        code.

4. You should check that the dev requirements are installed.
   This can be done by running the command
   ``pip install -e .[dev]`` from within the ``fitbenchmarking`` directory.
