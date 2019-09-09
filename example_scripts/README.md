# Example Scripts

Folder that holds all the example scripts for fitBenchmarking. The user can modify these files and run a benchmarking on their machine. For more details, please read the comments in the code of each file.

Here is the list of all the example scripts and the difference between them:
1. `example_runScripts.py` is designed to be the first script to run once FitBenchmarking is properly installed. This script will benchmark Scipy minimizers against NIST-type problem definition file. User should be able to run this script without having to install any other software or packages
2. `example_runScripts_mantid.py`is designed to be run once Mantid is installed on your computer. This script will benchmark Mantid minimizers against various different type of problem definition files.
3. `example_runScripts_expert.py` is designed to be run once Mantid and SasView (future development) are installed. This script will benchmark all the minimizers from different softwares against various type of problem definition files.
### Example usage

For default minimizers use (which loads fitbenchmarking_default_options.json):
`mantidpython example_runScripts.py`

Can also change the `minimizers` variable within `example_runScripts.py` to customize the minimization (see example script)

Optional load custom json file containing minimizers:
`mantidpython example_runScripts.py relative_path_to_json_file`
