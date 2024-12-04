.. _adding_data:

################
Adding More Data
################

We encourage users to contribute more data sets to FitBenchmarking;
the more data we have available to test against, the more useful
FitBenchmarking is. First, please ensure that there is a
:ref:`parser<problem_def>` available that can read your dataset, and if
necessary follow the :ref:`instructions to add this
functionality<parsers>` to FitBenchmarking.  Once this is done,
follow the steps below and add to a pull request to make the
data available to others.

1. Create a directory that contains:
   
   - the data sets to be included
     
   - a file `META.txt` containing metadata about the dataset.
     
   - a subfolder `data_files` which contains any supplemental data
     needed by the data parser.  We particularly encourage analytic
     derivative information, if available.

2. Update the :ref:`BenchmarkProblems` page to include a description of
   the dataset.  As well as information about the source of the data, this
   should include:

   - information about how many parameters and how many data points
     are to be fitted in the dataset
   
   - details of any external software that needs to be installed to load these
     datasets.
   
3. Create `zip` and `tar.gz` archives of these directories, and pass along
   to one of the core developers to put on the webspace.  They will pass you a
   location of the dataset to include in the description page, and update the
   folder containing all examples to contain your data set.

4. If the data is to be distributed with the GitHub source, add the directory to the
   `examples/benchmark_problems` folder and commit to the repository.  Please note
   that the maximum size of a file supported by GitHub is 100MB, and so datasets
   with files larger than this cannot be added to the repository.  Also, GitHub
   recommends that the size of a Git repository is not more than 1GB.



