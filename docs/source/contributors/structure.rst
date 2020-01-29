.. _structure:

#####################
Structure of the code
#####################


At the root of the repository there are four directories:
 - build
 - docs
 - examples
 - fitbenchmarking

***************
Build (`build`)
***************
This directory contains scripts to allow for installing packages such as Mantid
through setuptools.

**********************
Documentation (`docs`)
**********************
The documentation for FitBenchmarking is stored in this folder under `source`.
A local copy of the documentation can be build using `make html` in the `build`
directory.

*********************
Examples (`examples`)
*********************
Examples is used to store two sets of assets:
 - Problem files
 - Options files

A collection of problem files can be found organised into datasets withing the
`benchmark_problems` directory.
An options template file, and a prewritten options file to run a full set of
minimizers is also made available in the Examples directory.

*******************************************
FitBenchmarking Package (`fitbenchmarking`)
*******************************************

The main FitBenchmarking package is split across several directories
with the intention that it is easily extensible.
The majority of these directories are source code, with exceptions being
`HTML Templates`, `Mock Problems`, and `System Tests`.

Each file that contains source code will have a directory inside it called
`tests`, which contains all of the tests for that section of the code.

CLI (`cli`)
===========
The CLI directory is used to define all of the entry points into the software.
Currently this is just the main `fitbenchmarking` command.


Controllers (`controllers`)
===========================
In FitBenchmarking, controllers are used to interface with third party
minimizers.

The controllers directory holds a base controller class and all subclasses of
it in FitBenchmarking, each of which of which interfaces with a different
fitting package.
The base class is used to define an expected interface, new controllers can
then be added by following the instructions in :ref:`_controllers`.


Core (`core`)
=============
This directory holds all code central to FitBenchmarking.
For example, this manages calling the correct parser and controller, as well as
compiling the results into a data object.


HTML Templates (`HTML_templates`)
=================================
As mentioned above, this directory does not hold any source code.
Files in HTML Templates are used to create the resulting html pages, and are a
combination of css, html, and python files.
The python files in this directory are scripts to update the css and html
assets.


Mock Problems (`mock_problems`)
===============================
The mock problems are used in some tests where full problem files are required.
These are here so that the examples can be moved without breaking the tests.


Parsing (`parsing`)
===================
Parsing is very similar to the Controllers directory, in that it holds a base
parser and all the subclasses of it.
Each subclass implements a parser for a specific file format.
Information on adding new controllers can be found in :ref:`_parsers`.


Results Processing (`results_processing`)
=========================================
All files that are used to generate output are stored here.
This includes index pages, text/html tables, plots, and support pages.


System Tests (`systests`)
=========================
Currently the only system tests in FitBenchmarking are regression tests, which
are used to ensure that code changes do not change the accuracy results for a
subset of problems.


Utils (`utils`)
===============
Uility functions which do not fit into the above sections are collected in the
Utils directory.
This contains the Options, and FittingResults classes, as well as functions
for logging and directory creation.
