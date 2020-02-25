.. _why:

#####
Why?
#####


Consider the following figure:

.. figure:: ../../images/Fit_for_GEM_peak_1_1.png
   :alt: GEM experiment data
   :width: 100.0%

   GEM experiment data

The black crosses show data obtained from the `GEM
instrument <https://www.isis.stfc.ac.uk/Pages/gem.aspx>`_ at the ISIS Neutron and
Muon source. The scientists conducting the experiment know what function
they can use to fit their data and, by finding appropriate parameters,
they can understand more about the sample being analysed; the smooth,
green line in the figure is just such a best-fit line.


Specifically, in this figure we have found parameters which
fit the convolution of the Ikeda-Carpenter function

.. math:: \frac{\alpha}{2} \left[ (1-R)(\alpha t)^2 e^{-\alpha t} + 2R\frac{\alpha^2\beta}{(\alpha - \beta)^3} \right]

and a pseudo-Voigt function (which is itself a linear combination of a
Lorentzian and a Gaussian). In this example the values of the parameters
give us information about the intensity of the peak, the fast and slow
delay constants and the peak position, among other things.

Such a workflow plays a crucial role in the processing and analysis of
data at large research facilities, as it is
required for tasks as diverse as instrument calibration, refinement of
structures, and data analysis methods specific to different scientific
techniques. Mathematically, we can formulate this as a nonlinear
least-squares problem; specifically, given :math:`n` data points
:math:`(x_i, y_i)` (the crosses in the figure above), together
with errors on the values of :math:`y_i`, :math:`\sigma_i`, we solve

.. math:: {\boldsymbol{\beta}}^* = \arg \min_{{\boldsymbol{\beta}}} \underbrace{\sum_i \left( \frac{y_i - f({\boldsymbol{\beta}};x_i)}{\sigma_i} \right)^2}_{\chi^2({\boldsymbol{\beta}})},\label{eq:chi2}

where :math:`f({\boldsymbol{\beta}};x)` is the model we’re trying to
fit (the convolution of an Ikeda Carpenter and pseudo Voigt function in
the example above).

Usually the scientist will supply a starting guess,
:math:`{\boldsymbol{\beta}}_0`. She then has to *choose which software or
algorithm to use to fit the curve*. Different algorithms may be more or
less suited to a problem, depending on factors such as the architecture
of the machine, the availability of first and second derivatives, the
amount of data, the type of model being fitted, etc.
FitBenchmarking will help the scientist make an informed choice by
comparing runtime and accuracy of all available minimizers, on their
specific hardware, on problems from their science area, which will
ensure they are using the best tool for the job. We discuss the specific
FitBenchmarking paradigm in the Section :ref:`how`.

We have written FitBenchmarking to be useful to

-  **Scientists**, who want to know what is the best algorithm for fitting
   their model to data they might encounter, on their specific hardware;

-  **Scientific software developers**, who want to know what is the
   state-of-the-art in fitting software, what they should recommend as
   the default solver, and if it’s worth implementing a new method in
   their software; and

-  **Mathematicians** and **computer scientists**, who want to understand the
   types of problems where the current algorithms are not performing,
   and to have a route to expose newly developed methods to users.

FitBenchmarking is being developed by representatives from each of these
communities, and we hope the tool will not only be used by each of
these, but will also help foster fruitful interactions and
collaborations across the disciplines.

