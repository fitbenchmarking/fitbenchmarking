.. _fitting_results_extend:

#################################
 Extending Fitting Results class
#################################

The FittingResult class is used to store values from the benchmarking that are
required for the fitting reports.
If this needs to be extended to allow for additional statistics or improved
outputs the following should be considered:
- All FittingResult attributes required for reports should be saved with the
  checkpointer (:class:`~fitbenchmarking.utils.checkpoint.Checkpoint`).
  Care should be taken to add any attributes in the appropriate
  ``add_result/add_problem`` method to save the value and the ``load`` method
  to read the value back in.
- Any calculations should be performed when initialising the FittingResult.
  This reduces runtime in total for any regenerated reports.
- The checkpointer uses pickle. All data that is passed via this to the reports
  will need to be compatible with pickle.
