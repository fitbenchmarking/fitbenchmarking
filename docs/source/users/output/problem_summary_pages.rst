.. _problem_summary_page:

====================
Problem Summary Page
====================

The problem summary page can be used to give an overview of the problem and
solutions obtained.

Best Fit
********

Here you will see information about the function being fit and the parameters.

If plots are enabled (see :ref:`MakePlots`), they will be shown alongside 
the summary table.

There will be an expandable section for each cost function tested. The section
will contain a summary table which shows the initial and best parameter values.

Below the table, you will see the plots of the initial and best fit obtained
for that cost function. On the same plot, you will also see a scatter plot of 
the data that is fitted. 


Comparison
**********

Summary
-------

The main plot on the page shows a comparison of all fits at once.
This can be used to compare how cost functions perform for a problem accross
all minimizers.

This uses colours to identify the cost function for each fit and shows all fits
on a single graph. The best minimizer for each cost function is more pronounced
on the plot.

This should not be used to identify the best individual fit, but can be a good
indication of whether cost functions are biased to certain datapoints in the
input.

Residuals
---------

These plots show the residuals for each fit. The residuals are the difference
between the data and the fit. This can be used to identify how well the fit
matches the data. 

The residuals plots will be grouped by cost function. Each
plot/sub-plot will show the residuals for all minimizers used while
fitbenchmarking.

Multistart
----------

These plots are only visible for problems that are compatible with the multistart
feature. They show a summary of results grouped by each cost function, software
and minimizer. The traces on the plot are colour coded.

The successful runs are those where the **norm_acc** is within
the **multistart_success_threshold**. These traces are shaded blue. 

The unsuccessful runs are those where the **norm_acc** is above the threshold.
These traces are shaded red.
