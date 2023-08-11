# -*- coding: utf-8 -*-

import re
import subprocess
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from click import progressbar


class FispactError(Exception):
    pass


def run_fispact(input_file, files='files', cwd=None, verbose=False):
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


def run_tasks(task_list, verbose=False, threads=1):
    """Runs FISPACT calculations.

    Parameters
    ----------
    task_list : list
        List of tasks.
    verbose : bool
        Output verbosity. Default: True.
    threads : int
        The number of threads to execute. Default: 1.
    """
    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = [pool.submit(run_case, t) for t in task_list]
        with progressbar(length=len(futures)) as bar:
            for _ in concurrent.futures.as_completed(futures):
                bar.update(1)


def run_case(task_case):
    """Runs FISPACT calculations for the specific case.

    Parameters
    ----------
    task_case : tuple
        A tuple of tasks to be executed for one particular case.
        (cwd, tasks) - cwd - working directory (Path), tasks - list of tasks.
    """
    cwd, tasks = task_case
    for input_file in tasks:
        run_fispact(input_file, cwd=cwd)
