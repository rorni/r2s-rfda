# -*- coding: utf-8 -*-
import re
from pathlib import Path
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pkg_resources import resource_filename

import numpy as np


def read_template(temp_name):
    with open(resource_filename(__name__, 'data/' + temp_name)) as f:
        template = f.read()
    return template


files_temp = read_template('files.temp')
collapse_temp = read_template('collapse.temp')
condense_temp = read_template('condense.temp')


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


def create_fispact_input(name, cwd, template, *args, **kwargs):
    """Creates fispact input file from the template.

    Parameters
    ----------
    name : str
        Name of FISPACT input file to be created.
    cwd : Path
        Working directory. In this directory files will be created. The folder
        must exist.
    template : str
        Template string with format specifiers. 
    *args : list
        A list of positional symbols that are to be inserted into template.
    **kwargs : dict
        A dictionary of named symbols that are to be inserted into template.
    """
    text = template.format(*args, **kwargs)
    with open(cwd / name, mode='w') as f:
        f.write(text)


def create_arbflux_text(ebins, flux):
    """Creates file for fispact flux conversion to the 709 groups.

    Parameters
    ----------
    ebins : array_like[float]
        Energy bins in MeV.
    flux : array_like[float]
        Group flux.

    Returns
    -------
    arb_flux : str
        Text for arb_flux file.
    """
    ncols = 6
    text = []
    for i, e in enumerate(reversed(ebins)):
        s = '\n' if (i + 1) % ncols == 0 else ' '
        text.append('{0:.6e}'.format(e * 1.e+6))  # Because fispact needs
        text.append(s)                            # eV, not MeV
    text[-1] = '\n'
   
    for i, e in enumerate(reversed(flux)):
        s = '\n' if (i + 1) % ncols == 0 else ' '
        text.append('{0:.6e}'.format(e))
        text.append(s)
    text[-1] = '\n'
    text.append('1\n')
    text.append('total flux={0:.6e}'.format(np.sum(flux)))

    return ''.join(text)


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
