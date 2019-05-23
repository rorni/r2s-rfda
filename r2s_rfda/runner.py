# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from .interface import run_fispact


def create_single_task(title=None, material=None, volume=None, ebins=None,
                       flux=None, folder=None, fispact_settings=None):
    """Creates input files for FISPACT calculations.

    Parameters
    ----------
    title : str
        Title for the inventory case.
    material : Material
        Material to be irradiated.
    volume : float
        Volume of the material.
    ebins : array_like
        Energy bins of neutron group spectrum.
    flux : array_like
        Neutron group flux.
    fispact_settings : FispactSettings
        Settings for FISPACT code.

    Returns
    -------
    cwd : Path
        Working directory of task.
    """
    config = {
        'type': 'single',
        'title': title, 'material': material, 'volume': volume, 'ebins': ebins,
        'flux': flux, 'fispact_settings': fispact_settings
    }


def create_mesh_tasks(folder=None, fmesh=None, volumes=None,
                      fispact_settings=None, simple=False):
    """Creates input files for FISPACT calculations on mesh.

    There are two approaches. The first one is rigid - to calculate
    activation for all mesh voxels for all materials. But this approach is
    time consuming for large meshes. The second is to run one calculation
    for every material and for every energy group, and then to make a
    combination of the obtained results for every voxel. The latter approach
    may be inaccurate.

    Parameters
    ----------
    folder : str
        Folder.
    fmesh : FMesh
        Neutron flux mesh data.
    volumes : dict
        Volumes of cells with material for every voxel. (i, j, k, c)->volume
    fispact_settings : FispactSettings
        Settings of FISPACT calculations.
    simple : bool
        If True then simplified approach is used. Otherwise rigid approach is
        used. Default: True.

    Returns
    -------
    cwd : Path
        Working path for mesh calculations.
    """
    pass


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


