.. _problem_summary_page:

====================
Problem Summary Page
====================

The problem summary page can be used to give an overview of the problem and
solutions obtained.

Problem Outline
***************

First is the initial problem. Here you will see information about the function
being fit and the set of initial parameters used for the fitting.
If plots are enabled (see :ref:`MakePlots`), you will also see a scatter plot
of the data to fit with a line of the initial fit given to the minimizer.


Comparison
**********

The main plot on the page shows a comparison of all fits at once.
This can be used to compare how cost functions perform for a problem accross
all minimizers.

This uses colours to identify the cost function for each fit and shows all fits
on a single graph. The best minimizer for each cost function is more pronounced
on the plot.

This should not be used to identify the best individual fit, but can be a good
indication of whether cost functions are biased to certain datapoints in the
input.

Best Plots
**********

The page ends with an expandable section for each cost function tested, which
gives the parameter values and plot of the best fit obtained for that cost
function.
