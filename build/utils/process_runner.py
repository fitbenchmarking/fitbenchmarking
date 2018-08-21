"""
Wrapper for running subprocesses
"""

import subprocess

from build.utils.common import BUILD_LOGGER


def run_process_and_log(list_of_args):
    """
    Call a process using Popen and logs output to file.

    @param list_of_args :: list of arguments for Popen
    """
    process = subprocess.Popen(list_of_args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    process_output, process_error = process.communicate()
    exit_status = process.returncode
    if process_output:
        BUILD_LOGGER.logger.info(process_output)
    if exit_status != 0:
        BUILD_LOGGER.logger.error(process_error)
        return False
    return True


def run_process_with_shell(list_of_args):
    """
    Run a process using the shell true command and do not log the output.

    @param list_of_args :: list of args for Popen
    """

    subprocess.call(list_of_args, shell=True)
