.. _getting-started:

###############
Getting Started
###############

|Python 2.7+| will be needed for running/installing this. For instructions
on setting up python see :ref:`setting-up-python`.

  Note: If using Python 3, Mantid problems and minimizers will be unavailable.
  As such, you should skip step 4.

1. Download this repository or clone it using
   `git <https://git-scm.com/>`__:
   ``git clone https://github.com/mantidproject/fitbenchmarking.git``
2. Open up a terminal (command prompt) and go into the
   ``fitbenchmarking`` directory.
3. Once you are in the right directory, type
   ``pip install .``. If this doesn't work either ``pip`` is not
   in your PATH or not installed, then see instructions further below.
4. Install any additional softwares you wish to benchmark.
   See :ref:`install_instructions` for more information on this.
5. Finally run ``fitbenchmarking`` with a problem set from the examples
   folder.
   By default this will run fitbenchmarking with a variety of minimizers
   from several software packages.
   The result tables can be found in ``./results``.

.. |Python 2.7+| image:: https://img.shields.io/badge/python-2.7-blue.svg
   :target: https://www.python.org/downloads/release/python-2715/

.. _setting-up-python:

***************************
Setting up Python, pip etc.
***************************

Windows
=======

Download and Install Python
---------------------------

Download python
`2.7 <https://www.python.org/downloads/release/python-2717/>`__, or
`3 <https://www.python.org/downloads/release/python-380/>`__.
From the list at the bottom of the page, please select
``Windows x86 installer``. Double click and run the installer with
the default options.

Add Python and pip Directories to your Path Environment Variable
--------------------------------------------------------------

In order to make it so you can access Python via any command line prompt
(and not just the Python-specific one), you’ll need to add the
newly-installed Python directory to your “Path” system environment
variable. This makes it easier to access Python and run scripts in
whatever shell you’re using to using (Command Prompt, PowerShell or Git
Bash.) Go to Control Panel –> System Properties –> Environment Variables
and select the PATH variable from the list below:

.. figure:: ../../images/PathVariable.png
   :alt: Path Variable List

   Path Variable List

Click **edit** and append the Python path at the end of the string like
so:

.. figure:: ../../images/AppendingPath.png
   :alt: Appending Python Path

   Appending Python Path

If you are using Python 3, you should change this line accordingly.
Also make sure you include the
``C:\Python<version>\Scripts`` in the Path too even
if it doesn’t exist yet – this is where your package management tools (including pip),
unit testing tools, and other command line-accessible Python programs
will live.

Installing pip
--------------

Pip is a Python package management tool.

If for some reason pip is not installed on your system then e.g.
see `these detailed set of instructions on how to install it from
source <https://pip.pypa.io/en/latest/installing/>`__ .


Linux
=====

Python comes with the supported Linux versions of FitBenchmarking.

Setting up Pip
-----------------------------

It also usually has pip installed. If pip is not present in your system,
then, for example, on a debian version of Linux open a terminal and run
``sudo apt-get install python-pip``


*****************
Installing Pandoc
*****************

Pandoc is used to convert the HTML tables into RST format, see here `here <https://pandoc.org/installing.html>`__ for installation.
