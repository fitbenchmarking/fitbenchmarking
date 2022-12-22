.. _tutorials:

###############################
FitBenchmarking tutorial videos
###############################

On this page you will find some short tutorial videos on how to use FitBenchmarking.



Interpreting FitBenchmarking results
-------------------------------------

The following video explains how to interpret FitBenchmarking results.

.. raw:: html

    <video width="640" height="360" controls src="../_static/videos/FitBenchmarking_Tutorials-Interpreting_FitBenchmarking_results.webm">
        <track
        label="English"
        kind="subtitles"
        srclang="en"
        src="../_static/captions/Modified_AutoTranscript_FitBenchmarking_Tutorials-Interpreting_FitBenchmarking_results.vtt" />
    </video>

|

Running FitBenchmarking
----------------------------

The following video explains how to run FitBenchmarking.

.. raw:: html

   <video width="640" height="360" controls src="../_static/videos/FitBenchmarking_Tutorials-Running_FitBenchmarking.webm">
        <track
        label="English"
        kind="subtitles"
        srclang="en"
        src="../_static/captions/Modified_AutoTranscript_FitBenchmarking_Tutorials-Running_FitBenchmarking.vtt" />
    </video>


Useful links:
^^^^^^^^^^^^^
`www.python.org/downloads/ <https://www.python.org/downloads/>`_

Code demonstrated in this video:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python -m pip install fitbenchmarking[bumps,DFO,gradient_free,minuit,SAS,numdifftools]

.. code-block:: bash

   fitbenchmarking

.. code-block:: bash

   fitbenchmarking -p examples/benchmark_problems/NIST/low_difficulty

.. code-block:: bash

   fitbenchmarking -o examples/options_template.ini

.. code-block:: bash

   fitbenchmarking -r new_results/

.. code-block:: bash

   fitbenchmarking -t acc runtime

.. code-block:: bash

   fitbenchmarking -t acc -l WARNING

|

Choosing your options
----------------------------

The following video explains how to choose the best cost function / software / minimizer / Jacobian / Hessian for your data.

.. raw:: html

    <video width="640" height="360" controls src="../_static/videos/FitBenchmarking_Tutorials-Choosing_your_options.mp4">
        <track
        label="English"
        kind="subtitles"
        srclang="en"
        src="../_static/captions/Modified_AutoTranscript_FitBenchmarking_Tutorials-Choosing_your_options.vtt" />
    </video>