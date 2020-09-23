.. _problem_def:

************************
Problem Definition Files
************************

In FitBenchmarking, problems can be defined using several file formats.
The ``examples/benchmark_problems`` directory holds a collection of these
that can be used for reference.

More information on the supported formats can be found on the following pages.

.. toctree::
    :titlesonly:
    :maxdepth: 2
    :caption: File Formats:

    cutest
    native
    multifit
    nist

Detecting problem file type
===========================

FitBenchmarking detects which parser to use in two ways:

    - For the CUTEst file format we check that the extension of the data file is `sif`
    - For native and NIST file formats we check the first line of the file

        - `# FitBenchmark Problem` corresponds to the native format
        - `# NIST/ITL StRD` corresponds to the NIST format
