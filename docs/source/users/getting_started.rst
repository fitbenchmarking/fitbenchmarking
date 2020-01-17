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
   ``pip install .``.
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

******************
Setting up Python
******************

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

Add the Python Directory to your Path Environment Variable
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
if it doesn’t exist yet – this is where your package management tools,
unit testing tools, and other command line-accessible Python programs
will live.

Installing pip
--------------

There’s a couple of different options for package management in Python,
here we are going to use pip. Pip makes it trivial for us to install
Python packages, like ``setuptools``. You are going to have to install
packages pretty often if we’re working with third party tools and
libraries, so this is a must-have.

`Pip has a detailed set of instructions on how to install it from
source <https://pip.pypa.io/en/latest/installing/>`__ – if you don’t
have the curl command on your system, just use your Git or even your web
browser to download the source file mentioned in their instructions.

Installing setuptools
---------------------

Installing setuptools, which will be needed for installing the
fitbenchmarking package, is straight forward. If pip installed
succesfully, just run: ``pip install setuptools``

This concludes the python installation guide for Windows 7/10.

Linux
=====

Python comes with the supported versions of Ubuntu (18.04 or 16.04).

Setting up Pip and Setuptools
-----------------------------

It also usually has pip installed. If pip is not present in your system,
please open a terminal and run ``sudo apt-get install python-pip``
Following this, to get the setuptools package run
``sudo pip install python-setuptools``

This concludes the python installation guide for Ubuntu 16.04/18.04.


*****************
Installing Pandoc
*****************

Pandoc is used to convert the HTML tables into RST format, see here `here <https://pandoc.org/installing.html>`__ for installation.
