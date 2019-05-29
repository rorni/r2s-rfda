# -*- coding: utf-8 -*-

import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from . import utils


class FispactError(Exception):
    pass


def run_fispact(input_file, files='files', cwd=None, verbose=True):
    """Runs FISPACT code.

    If run ends with errors, then FispactError exception is raised.

    Parameters
    ----------
    input_file : str
        The name of input file.
    files : str
        The name of FISPACT files file. Default: 'files'.
    cwd : Path-like or str
        Working directory. Default: None.
    verbose : bool
        Whether to print calculation status to stdout.

    Returns
    -------
    status : str
        Run status message.
    """
    status = subprocess.check_output(
        ['fispact', input_file, files], encoding='utf-8', cwd=cwd
    )
    if verbose:
        print(status)
    check_fispact_status(status)
    return status


def check_fispact_status(text):
    """Raises FispactError exception if FATAL ERROR presents in output.

    Parameters
    ----------
    text : str
        Text to be checked.
    """
    match = re.search('^.*run +terminated.*$', text, flags=re.MULTILINE)
    if match:
        raise FispactError(match.group(0))


def run_tasks(folder, verbose=True, threads=1):
    """Runs FISPACT calculations.

    Parameters
    ----------
    folder : str or Path
        Folder with files to run.
    verbose : bool
        Output verbosity. Default: True.
    threads : int
        The number of threads to execute.
    """
    # TODO: Insert loading of configuration

    condense_name, condense_files = condense_task
    run_fispact(condense_name, condense_files, cwd=cwd, verbose=verbose)

    with ThreadPoolExecutor(max_workers=threads) as pool:
        pool.map(partial(_run_case, verbose=verbose), flux_tasks)


def _run_case(case_todo, verbose=True):
    """Runs FISPACT calculations for the specific case.

    Parameters
    ----------
    case_todo : dict
        A dictionary of tasks to do in the case. It contains following keys:
        'cwd' - working directory of the case, 'task_list' - a list of tuples
        (task_file_name, task_files).
    verbose : bool
        Turns on verbose output. Default: True.
    """
    cwd = case_todo['cwd']
    task_list = case_todo['task_list']
    for input_file, files in task_list:
        run_fispact(input_file, files=files, cwd=cwd, verbose=verbose)
