# FitBenchmarking Main Code
## Usage

The fitBenchmarking scripts can be run from the `example_scripts` folder. For more details on how to do this, please check the documentation in the root directory readme. Alternatively, please read the [wiki](https://github.com/mantidproject/fitbenchmarking/wiki).

## Code Structure

The following psuedocode demonstrates how the benchmarking scripts work:

> User input from `example_scripts` is passed onto `fitting_benchmarking.py`

> > The fit problem details are read using the modules in `parsing/` and passed onto `fitbenchmark_one_problem.py`

> > Each minimizer for the tested software in `minimizers.json` is benchmarked against each considered problem.

> > > For each problem:

> > > > Fitting and benchmarking is done in the `main.py` file of the respective software folder in `fitting/`.

> > > > Results are stored in an object and passed back to the higher modules.

> > > An array of result objects is returned for one problem.

> > Array of arrays of objects returned to `example_scripts`

> The main module `results_output` uses the modules in `resproc/` to produce the final tables and support pages with all the results.
