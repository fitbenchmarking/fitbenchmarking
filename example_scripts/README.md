# Example Scripts

Folder that holds all the example scripts for fitBenchmarking. The user can modify these files and run a benchmarking on their machine. For more details, please read the comments in the code of each file.

### Example usage

For default minimizers use (which loads minimizers_list_defaults.json):
`mantidpython example_runScripts.py`

Can also change the `minimizers` variable within `example_runScripts.py` to customize the minimization (see example script)

Optional load custom json file containing minimizers:
`mantidpython example_runScripts.py relative_path_to_json_file`
