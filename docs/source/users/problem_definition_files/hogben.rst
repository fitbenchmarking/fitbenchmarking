.. _hogben_format:

******************
HOGBEN File Format
******************

The HOGBEN file format is based on :ref:`native`, this page is intended to
demonstrate where the format differs.

Examples of HOGBEN problems are:

.. literalinclude:: ../../../../examples/benchmark_problems/HOGBEN_samples/simple_sample.txt

.. literalinclude:: ../../../../examples/benchmark_problems/HOGBEN_samples/thin_layer_sample_1.txt

.. literalinclude:: ../../../../examples/benchmark_problems/HOGBEN_samples/similar_sld_sample_1.txt

As in the native format, an input file must start with a comment indicating
that it is a FitBenchmarking problem followed by a number of key value pairs.
Available keys can be seen in :ref:`native` and below:

software, name, description
  As described in the native format.

function
  The function is defined by a refnx model, which should be provided in the pickle
  data format (as described [here](https://refnx.readthedocs.io/en/v0.1.41/faq.html#can-i-save-models-objectives-to-file)). Starting values for the varying model parameters are defined within
  the model object.