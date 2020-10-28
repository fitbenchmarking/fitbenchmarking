.. _structure:

********************
Repository Structure
********************

At the root of the repository there are six directories:

 - build
 - Docker
 - docs
 - examples
 - fitbenchmarking
 - travis


#################
Build (``build``)
#################

This directory contains scripts to allow for installing packages such as Mantid
through setuptools.

###################
Docker (``Docker``)
###################

The continuous integration process on travis currently run on a Docker container,
and this directory holds the Dockerfiles.  The Docker containers are hosted on
Dockerhub.

``BasicInstall`` holds the Dockerfile that is pushed to the repository ``fitbenchmarking/fitbenchmarking-deps``, the lastest of which should have the tag ``latest``.  This contains a basic Ubuntu install, with just the minimal infrastructure needed to run the tests.

``FullInstall`` holds the Dockerfile that is pushed to the repository ``fitbenchmarking/fitbenchmarking-extras``, the lastest of which should have the tag ``latest``.  This is built on top of the basic container, and includes optional third party software that FitBenchmarking can work with.

The versions on Docker Hub can be updated from a connected account by issuing the commands:

.. code-block:: bash

		docker build --tag fitbenchmarking-<type>:<tag>
		docker tag fitbenchmarking-<type>:<tag> fitbenchmarking/fitbenchmarking-<type>:<tag>
		docker push fitbenchmarking/fitbenchmarking-<type>:<tag>

where ``<type>`` is, e.g., ``deps`` or ``extras``, and ``<tag>`` is, e.g., ``latest``.

########################
Documentation (``docs``)
########################

The documentation for FitBenchmarking is stored in this folder under
``source``.
A local copy of the documentation can be build using ``make html`` in the
``build`` directory.


#######################
Examples (``examples``)
#######################

Examples is used to store sample problem files and options files.

A collection of problem files can be found organised into datasets within the
``examples/benchmark_problems/`` directory.

An options template file and a prewritten options file to run a full set of
minimizers is also made available in the ``examples/`` directory.


###################################################
FitBenchmarking Package (:py:mod:`fitbenchmarking`)
###################################################

The main FitBenchmarking package is split across several directories
with the intention that it is easily extensible.
The majority of these directories are source code, with exceptions being
Templates, Mock Problems, and System Tests.

Each file that contains source code will have a directory inside it called
``tests``, which contains all of the tests for that section of the code.


Benchmark Problems (``benchmark_problems``)
===========================================

This is a copy of the NIST benchmark problems from `examples/benchmark_problems`.
These are the default problems that are run if no problem is passed to the
``fitbenchmarking`` command, and is copied here so that it is distributed
with the package when installed using, say, `pip`.



CLI (:py:mod:`~fitbenchmarking.cli`)
====================================

The CLI directory is used to define all of the entry points into the software.
Currently this is just the main `fitbenchmarking` command.


Controllers (:py:mod:`~fitbenchmarking.controllers`)
====================================================

In FitBenchmarking, controllers are used to interface with third party
minimizers.

The controllers directory holds a base controller class
(:class:`~fitbenchmarking.controllers.base_controller.Controller`) and all its subclasses,
each of which of which interfaces with a different fitting package.  The controllers
currently implemented are described in :ref:`fitting_option` and :ref:`minimizer_option`.

New controllers can be added by following the instructions in :ref:`controllers`.


Core (:py:mod:`~fitbenchmarking.core`)
======================================

This directory holds all code central to FitBenchmarking.
For example, this manages calling the correct parser and controller, as well as
compiling the results into a data object.

Jacobian (:py:mod:`~fitbenchmarking.jacobian`)
==============================================

This directory holds the :class:`~fitbenchmarking.jacobian.base_jacobian.Jacobian` class,
and subclasses, which are used by the controllers to approximate derivatives.
Currenlty available options are described in :ref:`fitting_option`, and new
numerical Jacobians can be added by following the instructions in
:ref:`jacobian_extend`.


Mock Problems (``mock_problems``)
=================================

The mock problems are used in some tests where full problem files are required.
These are here so that the examples can be moved without breaking the tests.


Parsing (:py:mod:`~fitbenchmarking.parsing`)
============================================

The parsers read raw data into a format that FitBenchmarking can use.
This directory holds a base parser,
:class:`~fitbenchmarking.parsing.base_parser.Parser` and all its subclasses.
Each subclass implements a parser for a specific file format.
Information about existing parsers can be found in :ref:`problem_def`, and
see :ref:`parsers` for instructions on extending these.


Results Processing (:py:mod:`~fitbenchmarking.results_processing`)
==================================================================

All files that are used to generate output are stored here.
This includes index pages, text/html tables, plots, and support pages.
Information about the tables we provide can be found in
:ref:`output`, and instructions on how to add further tables and change
the formatting of the displayed information can be found in :ref:`extending_outputs`.

System Tests (``systests``)
===========================

FitBenchmarking runs regression tests to check that the
accuracy results do not change with updates to the code.
These tests run fitbenchmarking against a subset of problems
(in subdirectories of `/fitbenchmarking/mock_problems/`),
and compares the text output with that stored in
`/fitbenchmarking/systests/expected_results/`.

Templates (``templates``)
=========================

Files in Templates are used to create the resulting html pages, and are a
combination of css, html, and python files.
The python files in this directory are scripts to update the css and html
assets.
Instructions on updating these can be found in :ref:`templates`.

Utils (:py:mod:`~fitbenchmarking.utils`)
========================================

This directory contains utility functions that do not fit into the
above sections.
This includes the :class:`~fitbenchmarking.utils.options.Options`
class (see :ref:`options_extend` to extend)
and :class:`~fitbenchmarking.utils.fitbm_result.FittingResult` class,
as well as functions for logging and directory creation.

###################
Travis (``travis``)
###################

We use `Travis <https://travis-ci.org/github/fitbenchmarking/fitbenchmarking>`_
to run our Continuous Integration tests.
The specific tests run are defined in a series of Bash scripts,
which are stored in this folder.
